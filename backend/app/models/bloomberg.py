"""International tables parsed from the daily Bloomberg .xlsx export.

Layout follows page 2's right column: rate curves (SOFR, EURO STR,
EURIBOR, HIBOR CNH, SHIBOR CNY, RUONIA), FX crosses (modelled in fx.py),
commodities, equity indices and US treasuries.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.common import SourceMeta
from app.models.fx import FxCrossTable


class RateCurveRow(BaseModel):
    """One date row of a benchmark-rate curve table (O/N..12M)."""

    date: str
    on: Optional[float] = None
    m1: Optional[float] = None
    m3: Optional[float] = None
    m6: Optional[float] = None
    m12: Optional[float] = None


class RateCurveTable(BaseModel):
    """A named benchmark curve, e.g. 'СТАВКА USD SOFR (%)'."""

    name: str
    rows: List[RateCurveRow] = Field(default_factory=list)


class Commodity(BaseModel):
    """СЫРЬЕВОЙ РЫНОК row: price + 1m/6m/12m changes."""

    name: str
    price: Optional[float] = None
    change_1m: Optional[float] = None
    change_6m: Optional[float] = None
    change_12m: Optional[float] = None


class CommodityTable(BaseModel):
    rows: List[Commodity] = Field(default_factory=list)


class EquityIndex(BaseModel):
    """ИНДЕКСЫ ФОНДОВОГО РЫНКА row: price + 1m/6m/12m changes."""

    name: str
    price: Optional[float] = None
    change_1m: Optional[float] = None
    change_6m: Optional[float] = None
    change_12m: Optional[float] = None


class EquityIndexTable(BaseModel):
    rows: List[EquityIndex] = Field(default_factory=list)


class TreasuryRow(BaseModel):
    """ОБЛИГАЦИИ КАЗНАЧЕЙСТВА США row: tenor + yield + changes."""

    tenor: str
    yld: Optional[float] = None
    change_1m: Optional[float] = None
    change_6m: Optional[float] = None
    change_12m: Optional[float] = None


class TreasuryTable(BaseModel):
    rows: List[TreasuryRow] = Field(default_factory=list)


class BloombergData(BaseModel):
    """Everything parsed from one daily Bloomberg export."""

    rate_curves: List[RateCurveTable] = Field(default_factory=list)
    fx: FxCrossTable
    commodities: CommodityTable
    equities: EquityIndexTable
    treasuries: TreasuryTable
    meta: SourceMeta
