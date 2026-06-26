"""Editable layout/style configuration ("Design mode").

Every visual token the newsletter template uses for colours, typography,
spacing, borders and the watermark lives here. The frontend's Design mode
edits these, the backend persists them to config/layout.json, and the
template renders from them. Defaults reproduce the pixel-matched reference,
so a fresh install looks identical until someone customises it.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# Font families embedded in assets/fonts (see rendering/fonts.py).
FontName = Literal[
    "Bebas", "Oswald", "Montserrat", "NotoSans", "Lora", "Tinos", "OpenSansIt"
]


class LayoutConfig(BaseModel):
    """All tunable design tokens. Field defaults == the reference look."""

    # --- Colours ------------------------------------------------------------
    accent_gold: str = "#f4e7d4"     # caption / summary / highlight fill
    page_bg: str = "#faf4ea"         # parchment base
    gold_line: str = "#c6a667"       # gold outlines: cards, oval, badge
    gold_text: str = "#c0955d"       # the issue-date gold
    card_bg: str = "#fbf8f1"         # opaque cream card
    table_border: str = "#6f6a5e"    # table outer border
    grid: str = "#b9b3a3"            # table cell borders
    pill_line: str = "#1c1c1c"       # section-pill outline
    ink: str = "#000000"             # body text

    # --- Fonts (must be one of the embedded families) -----------------------
    display_font: FontName = "Bebas"     # title + section headers
    headline_font: FontName = "Lora"     # news lead + table captions
    body_font: FontName = "NotoSans"     # labels, column heads, body
    table_font: FontName = "Tinos"       # table data (Times-compatible)

    # --- Typography sizes (pt; A3 maps 1:1 to the reference) ----------------
    title_size: float = 38.5
    date_size: float = 11.7
    dept_size: float = 13.8
    pill_size: float = 23.5
    news_size: float = 12.0
    col_head_size: float = 19.7
    section_head_size: float = 19.7
    caption_size: float = 9.6
    table_size: float = 8.6
    summary_value_size: float = 15.0
    footnote_size: float = 9.0

    # --- Spacing (pt unless noted) ------------------------------------------
    page_padding_mm: float = 6.0
    quad_gap: float = 19.0
    card_padding: float = 13.0
    table_gap: float = 7.0

    # --- Borders (pt) -------------------------------------------------------
    card_border_w: float = 1.6
    table_border_w: float = 1.0

    # --- Watermark ----------------------------------------------------------
    background_placement: Literal["watermark", "none"] = "watermark"
    background_opacity: float = Field(0.05, ge=0.0, le=1.0)
    background_grayscale: float = Field(0.5, ge=0.0, le=1.0)

    # --- Section toggles ----------------------------------------------------
    show_capital_news: bool = True
    show_footnote: bool = True
    show_charts: bool = True
