"""Telegram news drafts (region-routed).

Pulls recent text posts from configured news channels and routes each
channel's latest posts into a newsletter region (US / Europe / Asia / CIS /
capital_markets) using `telegram_news_channel_map`. Output is plain editable
draft text — nothing is auto-published; staff edit it in the textboxes.

Uses Telethon (MTProto), same as the stock fetcher. Degrades to empty drafts
whenever Telethon, a session, or the config is missing — never raises.
"""

from __future__ import annotations

from app.core.config import get_settings

REGIONS = ("us", "europe", "asia", "cis", "capital_markets")


def _empty() -> dict[str, list[str]]:
    return {r: [] for r in REGIONS}


async def fetch_news_drafts(per_channel: int | None = None) -> dict[str, list[str]]:
    """Return {region: [draft post, ...]}. Empty until configured/available."""
    settings = get_settings()
    drafts = _empty()

    channels = settings.telegram_news_channels
    if not (settings.telegram_api_id and settings.telegram_api_hash and channels):
        return drafts

    try:
        from telethon import TelegramClient  # optional dependency
    except ImportError:
        return drafts

    limit = per_channel or settings.telegram_news_per_channel
    mapping = settings.telegram_news_channel_map or {}

    client = TelegramClient(
        settings.telegram_session, settings.telegram_api_id, settings.telegram_api_hash
    )
    try:
        await client.connect()
        if not await client.is_user_authorized():
            return drafts
        for ch in channels:
            region = mapping.get(str(ch), "")
            if region not in REGIONS:
                # Unmapped channel: drop into capital_markets as a catch-all.
                region = "capital_markets"
            try:
                entity = await client.get_entity(ch)
                async for msg in client.iter_messages(entity, limit=limit):
                    text = (msg.message or "").strip()
                    if text:
                        drafts[region].append(text)
            except Exception:  # noqa: BLE001 - skip a bad channel, keep going
                continue
        return drafts
    except Exception:  # noqa: BLE001 - degrade quietly
        return _empty()
    finally:
        await client.disconnect()
