"""CBU currency-rate fetcher.

Pulls the Central Bank of Uzbekistan public JSON feed
(https://cbu.uz/ru/arkhiv-kursov-valyut/json/). The feed supports
per-currency and per-date params:

    /json/                -> all currencies, latest
    /json/USD/            -> single currency, latest
    /json/all/2024-01-15/ -> all currencies on a date

We surface the configured subset (USD/EUR/RUB/CNY/GBP) as `<code>UZS` rows.
The 1m/6m/12m changes are computed by re-querying historical dates; if any
of those queries fail we leave the change blank (still editable) rather
than failing the whole table.

Degrades gracefully: on total failure returns last-known-good (STALE) or an
empty manual grid (EMPTY) — never raises.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

import httpx

from app.core import cache
from app.core.config import get_settings
from app.models.common import FetchStatus, SourceMeta
from app.models.fx import CbuFxTable, CbuRate

_CACHE_KEY = "cbu_currency"


def _date_url(base: str, d: Optional[date]) -> str:
    base = base.rstrip("/")
    if d is None:
        return f"{base}/"
    return f"{base}/all/{d.isoformat()}/"


def _index_by_code(feed: list[dict]) -> dict[str, dict]:
    return {row.get("Ccy", "").upper(): row for row in feed if row.get("Ccy")}


def _to_float(raw) -> Optional[float]:
    if raw in (None, "", "-"):
        return None
    try:
        return float(str(raw).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _pct_change(now: Optional[float], then: Optional[float]) -> Optional[float]:
    if now is None or then in (None, 0):
        return None
    return round((now - then) / then * 100.0, 2)


def _fetch_feed(client: httpx.Client, url: str) -> list[dict]:
    resp = client.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else []


def fetch(
    currencies: Optional[list[str]] = None,
    on_date: Optional[date] = None,
) -> CbuFxTable:
    settings = get_settings()
    currencies = currencies or settings.cbu_currencies
    base = settings.cbu_json_url
    today = on_date or date.today()

    fetched_at = datetime.utcnow().isoformat()

    try:
        with httpx.Client(timeout=settings.http_timeout) as client:
            latest = _index_by_code(_fetch_feed(client, _date_url(base, on_date)))

            # Historical snapshots for change columns (best-effort each).
            history: dict[str, dict[str, dict]] = {}
            for label, delta in (("1m", 30), ("6m", 182), ("12m", 365)):
                try:
                    snap = _fetch_feed(
                        client, _date_url(base, today - timedelta(days=delta))
                    )
                    history[label] = _index_by_code(snap)
                except (httpx.HTTPError, ValueError):
                    history[label] = {}

        rows: list[CbuRate] = []
        for code in currencies:
            cur = latest.get(code.upper(), {})
            price = _to_float(cur.get("Rate"))
            rows.append(
                CbuRate(
                    code=f"{code.upper()}UZS",
                    price=price,
                    change_1m=_pct_change(
                        price, _to_float(history["1m"].get(code.upper(), {}).get("Rate"))
                    ),
                    change_6m=_pct_change(
                        price, _to_float(history["6m"].get(code.upper(), {}).get("Rate"))
                    ),
                    change_12m=_pct_change(
                        price, _to_float(history["12m"].get(code.upper(), {}).get("Rate"))
                    ),
                )
            )

        table = CbuFxTable(
            rows=rows,
            meta=SourceMeta(
                source="cbu.uz JSON",
                status=FetchStatus.OK,
                fetched_at=fetched_at,
            ),
        )
        cache.save(_CACHE_KEY, table.model_dump())
        return table

    except (httpx.HTTPError, ValueError) as exc:
        return _degrade(currencies, str(exc))


def _degrade(currencies: list[str], reason: str) -> CbuFxTable:
    """Serve last-known-good (STALE) or an empty manual grid (EMPTY)."""
    cached = cache.load(_CACHE_KEY)
    if cached:
        table = CbuFxTable.model_validate(cached)
        table.meta.status = FetchStatus.STALE
        table.meta.warning = f"Using cached rates — live fetch failed: {reason}"
        return table

    return CbuFxTable(
        rows=[CbuRate(code=f"{c.upper()}UZS") for c in currencies],
        meta=SourceMeta(
            source="cbu.uz JSON",
            status=FetchStatus.EMPTY,
            warning=f"CBU fetch failed and no cache — enter rates manually: {reason}",
        ),
    )
