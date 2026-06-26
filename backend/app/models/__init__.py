"""Pydantic schemas for the NBU newsletter generator.

Every fetcher returns one of these models. The `Field`-level metadata
(`warning`, `source`) lets the API surface degraded fetches to the UI
without ever crashing the whole generation.
"""

from app.models.common import FetchStatus, SourceMeta, ValueCell
from app.models.fx import CbuRate, CbuFxTable, FxCross, FxCrossTable
from app.models.money_market import (
    UzoniaRow,
    UzoniaTable,
    RepoRow,
    RepoTable,
    InterbankRow,
    InterbankTable,
    LiquiditySummary,
    MoneyMarketLocal,
)
from app.models.bloomberg import (
    RateCurveRow,
    RateCurveTable,
    Commodity,
    CommodityTable,
    EquityIndex,
    EquityIndexTable,
    TreasuryRow,
    TreasuryTable,
    BloombergData,
)
from app.models.stocks import StockRow, StockTable
from app.models.news import NewsBlocks
from app.models.timeseries import TimeSeries, ChartSet
from app.models.newsletter import Newsletter, NewsletterMeta

__all__ = [
    "FetchStatus",
    "SourceMeta",
    "ValueCell",
    "CbuRate",
    "CbuFxTable",
    "FxCross",
    "FxCrossTable",
    "UzoniaRow",
    "UzoniaTable",
    "RepoRow",
    "RepoTable",
    "InterbankRow",
    "InterbankTable",
    "LiquiditySummary",
    "MoneyMarketLocal",
    "RateCurveRow",
    "RateCurveTable",
    "Commodity",
    "CommodityTable",
    "EquityIndex",
    "EquityIndexTable",
    "TreasuryRow",
    "TreasuryTable",
    "BloombergData",
    "StockRow",
    "StockTable",
    "NewsBlocks",
    "TimeSeries",
    "ChartSet",
    "Newsletter",
    "NewsletterMeta",
]
