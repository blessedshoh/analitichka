"""Free-text news blocks (page 1) — human-written/edited each issue."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class NewsBlocks(BaseModel):
    us: str = ""
    europe: str = ""
    asia: str = ""
    cis: str = ""
    capital_markets: List[str] = Field(
        default_factory=list,
        description="1-2 capital-markets news items (page 2 footer block).",
    )
