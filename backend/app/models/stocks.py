"""Tashkent / UZCE stock-results table extracted from the Telegram photo.

'ИТОГИ ТОРГОВ НА ФОНДОВОМ РЫНКЕ' — ticker, prev/curr price, % change.
Rows are flagged when the Claude-extracted percent disagrees with the
server-recomputed one beyond tolerance.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.common import SourceMeta


class StockRow(BaseModel):
    ticker: str
    price_prev: Optional[float] = None
    price_curr: Optional[float] = None
    change_pct: Optional[float] = None          # as extracted
    change_pct_calc: Optional[float] = None      # server-recomputed
    flagged: bool = False                         # extracted vs calc mismatch
    note: Optional[str] = None


class StockTable(BaseModel):
    rows: List[StockRow] = Field(default_factory=list)
    meta: SourceMeta
