"""Time-series feeding the four charts (re-plotted each issue)."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TimeSeries(BaseModel):
    """A labelled (date, value) series."""

    name: str
    dates: List[str] = Field(default_factory=list)
    values: List[Optional[float]] = Field(default_factory=list)


class ChartSet(BaseModel):
    """The data behind page-2 charts.

    `system_liquidity` -> red line; `cb_operations` -> green area;
    plus VIX and EMBI series.
    """

    system_liquidity: TimeSeries = Field(
        default_factory=lambda: TimeSeries(name="Общая ликвидность")
    )
    cb_operations: TimeSeries = Field(
        default_factory=lambda: TimeSeries(name="Операции ЦБ")
    )
    vix: TimeSeries = Field(default_factory=lambda: TimeSeries(name="VIX"))
    embi: TimeSeries = Field(default_factory=lambda: TimeSeries(name="EMBI"))
