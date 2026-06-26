"""Top-level Newsletter model: the single reviewed payload that renders.

The frontend assembles/edits every sub-model, then POSTs one Newsletter to
the generate endpoint. Nothing here is fetched at render time — by the time
it arrives it has already been human-reviewed.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models.bloomberg import BloombergData
from app.models.fx import CbuFxTable
from app.models.money_market import MoneyMarketLocal
from app.models.news import NewsBlocks
from app.models.stocks import StockTable
from app.models.timeseries import ChartSet


class NewsletterMeta(BaseModel):
    """Header band content."""

    title: str = "ОБЗОР РЫНКА"
    department: str = "ДЕПАРТАМЕНТ КАЗНАЧЕЙСТВА"
    weekday: str = ""                 # e.g. ВТОРНИК
    issue_date: str = ""              # e.g. 23.06.2026
    issue_number: Optional[int] = None


class Newsletter(BaseModel):
    meta: NewsletterMeta = Field(default_factory=NewsletterMeta)
    news: NewsBlocks = Field(default_factory=NewsBlocks)

    cbu_fx: Optional[CbuFxTable] = None
    money_market: Optional[MoneyMarketLocal] = None
    bloomberg: Optional[BloombergData] = None
    stocks: Optional[StockTable] = None
    charts: ChartSet = Field(default_factory=ChartSet)
