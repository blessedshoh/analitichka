"""Local money-market tables (page 2, left column).

Covers UZONIA tenor grid, REPO overview, interbank deposits and the
liquidity summary band. These come from the CBU scrape, which always has a
manual-entry fallback, so every field is optional and editable.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.common import SourceMeta


class UzoniaRow(BaseModel):
    """СТАВКА UZONIA (%): one date, tenors O/N..6M."""

    date: str
    on: Optional[float] = None
    w1: Optional[float] = None      # 1 week
    m1: Optional[float] = None      # 1 month
    m3: Optional[float] = None      # 3 month
    m6: Optional[float] = None      # 6 month


class UzoniaTable(BaseModel):
    rows: List[UzoniaRow] = Field(default_factory=list)
    meta: SourceMeta


class RepoRow(BaseModel):
    """Обзор рынка РЕПО: deals / average rate / volume per date."""

    date: str
    deals: Optional[int] = None
    avg_rate: Optional[float] = None
    volume: Optional[float] = None      # mln sum


class RepoTable(BaseModel):
    rows: List[RepoRow] = Field(default_factory=list)
    meta: SourceMeta


class InterbankRow(BaseModel):
    """МЕЖБАНКОВСКИЕ ДЕПОЗИТЫ: tenor / date / rate / trend / volume."""

    tenor: str
    date: str
    rate: Optional[float] = None
    trend: Optional[float] = None       # % change vs prior
    volume: Optional[float] = None      # mln sum


class InterbankTable(BaseModel):
    rows: List[InterbankRow] = Field(default_factory=list)
    meta: SourceMeta


class LiquiditySummary(BaseModel):
    """Общая ликвидность банковской системы band (4 figures)."""

    date: Optional[str] = None
    total_liquidity: Optional[float] = None             # trln, итог корр. счетов
    deviation_from_norm: Optional[float] = None         # trln
    cb_withdrawal_ops: Optional[float] = None           # trln, привлечение
    cb_provision_ops: Optional[float] = None            # предоставление
    meta: SourceMeta


class MoneyMarketLocal(BaseModel):
    """Bundle of every local money-market table for one issue."""

    uzonia: UzoniaTable
    repo: RepoTable
    interbank: InterbankTable
    summary: LiquiditySummary
