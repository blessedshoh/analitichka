"""Telegram stock-results fetcher + Claude vision extraction.

The Tashkent/UZCE 'ИТОГИ ТОРГОВ НА ФОНДОВОМ РЫНКЕ' table arrives as a PHOTO
in a public Telegram channel, never as text. Pipeline:

  1. Telethon (MTProto, NOT the Bot API — bots can't read channel history)
     downloads the latest matching image using a dedicated account session.
  2. The image is sent to the Anthropic Claude API (claude-sonnet-4-6) with a
     prompt demanding strict JSON: ticker / price_prev / price_curr /
     change_pct. The response is parsed defensively (code-fence stripping,
     try/except).
  3. change_pct is recomputed server-side from the two prices; rows whose
     extracted percent disagrees beyond tolerance are flagged.

Everything degrades to an empty editable grid; nothing raises.
"""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.config import get_settings
from app.models.common import FetchStatus, SourceMeta
from app.models.stocks import StockRow, StockTable

_PROMPT = (
    "You are extracting a stock-results table from an image. The table is "
    "titled 'ИТОГИ ТОРГОВ НА ФОНДОВОМ РЫНКЕ'. Columns are: ticker/name, "
    "previous-day price, current-day price, and percent change.\n\n"
    "Return ONLY a JSON array, no prose, no markdown fences. Each element:\n"
    '  {"ticker": str, "price_prev": number|null, '
    '"price_curr": number|null, "change_pct": number|null}\n'
    "Use a dot as the decimal separator. Preserve ticker text exactly "
    "(Latin/Cyrillic). If a cell is unreadable, use null."
)


# --------------------------------------------------------------------------- #
# Telegram download (Telethon, MTProto)
# --------------------------------------------------------------------------- #
async def download_latest_image(limit: int = 25) -> Optional[Path]:
    """Download the newest photo from the configured channel. None on failure."""
    settings = get_settings()
    if not (settings.telegram_api_id and settings.telegram_api_hash):
        return None
    if not settings.telegram_stock_channel:
        return None
    try:
        from telethon import TelegramClient  # imported lazily; optional dep
    except ImportError:
        return None

    out_dir = Path(settings.cache_dir) / "tg"
    out_dir.mkdir(parents=True, exist_ok=True)

    client = TelegramClient(
        settings.telegram_session, settings.telegram_api_id, settings.telegram_api_hash
    )
    try:
        await client.connect()
        if not await client.is_user_authorized():
            # Session not logged in — caller falls back to manual.
            return None
        entity = await client.get_entity(settings.telegram_stock_channel)
        async for msg in client.iter_messages(entity, limit=limit):
            if msg.photo:
                dest = out_dir / f"stocks_{msg.id}.jpg"
                await client.download_media(msg, file=str(dest))
                return dest
        return None
    except Exception:  # noqa: BLE001 - optional, degrade quietly
        return None
    finally:
        await client.disconnect()


# --------------------------------------------------------------------------- #
# Claude vision extraction
# --------------------------------------------------------------------------- #
def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    # Grab the first JSON array if extra prose slipped through.
    m = re.search(r"\[.*\]", text, re.DOTALL)
    return m.group(0) if m else text


def extract_table_from_image(image_path: str | Path) -> list[dict]:
    """Send the image to Claude and return parsed raw rows. [] on failure."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        return []
    try:
        import anthropic
    except ImportError:
        return []

    path = Path(image_path)
    media = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media,
                                "data": b64,
                            },
                        },
                        {"type": "text", "text": _PROMPT},
                    ],
                }
            ],
        )
        raw = "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        )
        parsed = json.loads(_strip_fences(raw))
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, Exception):  # noqa: BLE001
        return []


# --------------------------------------------------------------------------- #
# Validation + assembly
# --------------------------------------------------------------------------- #
def _to_float(v) -> Optional[float]:
    if v in (None, ""):
        return None
    try:
        return float(str(v).replace(",", ".").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def _build_rows(raw_rows: list[dict]) -> list[StockRow]:
    settings = get_settings()
    tol = settings.change_pct_tolerance
    rows: list[StockRow] = []
    for rec in raw_rows:
        prev = _to_float(rec.get("price_prev"))
        curr = _to_float(rec.get("price_curr"))
        extracted = _to_float(rec.get("change_pct"))
        calc = None
        if prev not in (None, 0) and curr is not None:
            calc = round((curr - prev) / prev * 100.0, 2)
        flagged = (
            extracted is not None
            and calc is not None
            and abs(extracted - calc) > tol
        )
        rows.append(
            StockRow(
                ticker=str(rec.get("ticker", "")).strip(),
                price_prev=prev,
                price_curr=curr,
                change_pct=extracted,
                change_pct_calc=calc,
                flagged=flagged,
                note="extracted % differs from recomputed" if flagged else None,
            )
        )
    return rows


async def fetch() -> StockTable:
    """Full pipeline: download -> extract -> validate. Degrades to empty."""
    image = await download_latest_image()
    if image is None:
        return StockTable(
            rows=[],
            meta=SourceMeta(
                source="Telegram + Claude",
                status=FetchStatus.MANUAL,
                warning="No Telegram session/config or no image found — enter manually.",
            ),
        )
    return extract_from_path(image)


def extract_from_path(image_path: str | Path) -> StockTable:
    """Synchronous helper: extract+validate an already-downloaded image."""
    raw = extract_table_from_image(image_path)
    if not raw:
        return StockTable(
            rows=[],
            meta=SourceMeta(
                source="Telegram + Claude",
                status=FetchStatus.MANUAL,
                warning="Claude extraction returned nothing — enter/upload manually.",
            ),
        )
    rows = _build_rows(raw)
    flagged_n = sum(1 for r in rows if r.flagged)
    return StockTable(
        rows=rows,
        meta=SourceMeta(
            source="Telegram + Claude (claude-sonnet-4-6)",
            status=FetchStatus.OK,
            warning=(f"{flagged_n} row(s) flagged: review highlighted % values."
                     if flagged_n else None),
            fetched_at=datetime.utcnow().isoformat(),
        ),
    )
