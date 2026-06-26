"""Capital-market bond tables (page 2, РЫНОК КАПИТАЛА section).

These have no live feed (sourced from exchange/Bloomberg/manual entry) and
their columns differ per table, so they use a generic title+columns+rows
shape that the UI edits as a free grid and the template renders directly.

Slots fix their placement in the layout:
  corp_bonds       -> left column, sub-left   (КОРПОРАТИВНЫЕ ОБЛИГАЦИИ)
  gov_bonds        -> left column, sub-right   (ИТОГИ РАЗМЕЩЕНИЯ ГОС.ОБЛИГАЦИЙ)
  eurobonds_fx     -> right column, sub-left   (ЕВРООБЛИГАЦИИ В ИН. ВАЛЮТЕ)
  eurobonds_local  -> right column, sub-left   (ЕВРООБЛИГАЦИИ В НАЦ. ВАЛЮТЕ)
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class CapitalTable(BaseModel):
    slot: str
    title: str
    columns: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
