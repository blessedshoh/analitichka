"""Telegram news drafts + refresh-all assembly (offline-safe)."""

import asyncio

from app.fetchers import telegram_news
from app import sample_data


def test_news_drafts_empty_without_config():
    drafts = asyncio.run(telegram_news.fetch_news_drafts())
    assert set(drafts) == set(telegram_news.REGIONS)
    assert all(v == [] for v in drafts.values())


def test_sample_has_capital_tables():
    nl = sample_data.sample_newsletter()
    slots = {t.slot for t in nl.capital_tables}
    assert {"corp_bonds", "gov_bonds", "eurobonds_fx", "eurobonds_local"} <= slots
    # every row matches its column count (renders cleanly)
    for t in nl.capital_tables:
        assert all(len(r) == len(t.columns) for r in t.rows)
