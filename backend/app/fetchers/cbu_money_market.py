"""CBU money-market fetcher (UZONIA, REPO overview, interbank deposits).

There is no documented feed, so we scrape cbu.uz. CBU redesigns its site
periodically, so the scrape is deliberately defensive and ALWAYS falls back
to an empty, fully-editable manual grid. The UI treats every value as a
draft requiring confirmation.

Public-facing function: `fetch()` returns a `MoneyMarketLocal` whose meta
status tells the UI whether anything was scraped or it's manual-only.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import httpx

from app.core.config import get_settings
from app.models.common import FetchStatus, SourceMeta
from app.models.money_market import (
    InterbankTable,
    LiquiditySummary,
    MoneyMarketLocal,
    RepoTable,
    UzoniaTable,
)

# Known CBU pages (subject to change — scrape parsing is best-effort).
_UZONIA_PAGE = "/ru/uzonia/"
_REPO_PAGE = "/ru/monetary-policy/operations/"


def _empty_manual(reason: str) -> MoneyMarketLocal:
    """The always-available fallback: blank editable grids."""
    meta = SourceMeta(
        source="cbu.uz scrape",
        status=FetchStatus.MANUAL,
        warning=reason,
        fetched_at=datetime.utcnow().isoformat(),
    )
    return MoneyMarketLocal(
        uzonia=UzoniaTable(rows=[], meta=meta.model_copy()),
        repo=RepoTable(rows=[], meta=meta.model_copy()),
        interbank=InterbankTable(rows=[], meta=meta.model_copy()),
        summary=LiquiditySummary(meta=meta.model_copy()),
    )


def _try_scrape(client: httpx.Client) -> Optional[MoneyMarketLocal]:
    """Attempt the live scrape. Returns None if structure isn't recognised.

    Implemented defensively: we fetch the pages so a future maintainer can
    wire concrete selectors, but if anything about the markup is unexpected
    we return None and let the caller fall back to the manual grid. This
    keeps the scrape from ever raising into generation.
    """
    settings = get_settings()
    try:
        # Touch the pages so connectivity/redesign issues surface here.
        client.get(settings.cbu_base_url + _UZONIA_PAGE)
        client.get(settings.cbu_base_url + _REPO_PAGE)
    except httpx.HTTPError:
        return None

    # NOTE: CBU's money-market figures are rendered in JS widgets / PDFs that
    # change shape often. Rather than ship a brittle selector that silently
    # yields wrong numbers into a *published financial table*, we treat this
    # source as manual-confirm by default. The hook above is where concrete
    # parsing goes once a stable endpoint is identified.
    return None


def fetch() -> MoneyMarketLocal:
    settings = get_settings()
    try:
        with httpx.Client(
            timeout=settings.http_timeout,
            headers={"User-Agent": "Mozilla/5.0 (NBU-newsletter)"},
        ) as client:
            scraped = _try_scrape(client)
    except httpx.HTTPError as exc:
        return _empty_manual(f"CBU unreachable — enter money-market data manually: {exc}")

    if scraped is not None:
        return scraped

    return _empty_manual(
        "CBU money-market figures require manual confirmation "
        "(no stable feed; scrape disabled to avoid publishing wrong data)."
    )
