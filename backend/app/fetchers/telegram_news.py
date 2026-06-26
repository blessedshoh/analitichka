"""Telegram news extension point (NOT core yet).

Clean hook to later pull recent text posts from configured news channels and
pre-fill the editable news textboxes as drafts. Returns plain dicts keyed by
the NewsBlocks regions so the frontend can drop them straight into textareas.

Today this is a no-op stub that returns empty drafts unless Telethon and a
session are configured; wiring the actual scrape is left for a future step.
"""

from __future__ import annotations

from typing import Optional

from app.core.config import get_settings


async def fetch_news_drafts(per_channel: int = 5) -> dict[str, list[str]]:
    """Return {region: [draft post, ...]}. Empty until implemented/configured."""
    settings = get_settings()
    drafts: dict[str, list[str]] = {
        "us": [], "europe": [], "asia": [], "cis": [], "capital_markets": []
    }
    if not (settings.telegram_api_id and settings.telegram_news_channels):
        return drafts

    # Extension point: iterate settings.telegram_news_channels with Telethon,
    # grab the last `per_channel` text messages, and route them into regions
    # (e.g. by channel->region mapping). Intentionally left unimplemented so
    # the contract is stable while the feature is built out.
    return drafts
