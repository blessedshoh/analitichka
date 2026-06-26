"""FX tables: local CBU rates (page 2, top-left) and international crosses."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.common import SourceMeta


class CbuRate(BaseModel):
    """One row of the local 'КУРСЫ ВАЛЮТ' table (UZS per unit)."""

    code: str = Field(..., description="e.g. USDUZS")
    price: Optional[float] = None
    change_1m: Optional[float] = None
    change_6m: Optional[float] = None
    change_12m: Optional[float] = None


class CbuFxTable(BaseModel):
    rows: List[CbuRate] = Field(default_factory=list)
    meta: SourceMeta


class FxCross(BaseModel):
    """One row of the international 'КУРСЫ ВАЛЮТ' table (e.g. EURUSD)."""

    code: str
    price: Optional[float] = None
    change_1m: Optional[float] = None
    change_6m: Optional[float] = None
    change_12m: Optional[float] = None


class FxCrossTable(BaseModel):
    rows: List[FxCross] = Field(default_factory=list)
    meta: SourceMeta
