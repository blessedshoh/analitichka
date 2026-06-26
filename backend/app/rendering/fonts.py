"""Embeds the newsletter's exact fonts as base64 @font-face rules.

The reference PDF uses Bebas Neue (display), Lora (serif captions/headlines),
Noto Sans (labels/body), Open Sans Italic (footnote) and Times New Roman
(table data). We ship metric-equivalent open fonts in assets/fonts/ — Tinos
is metrically compatible with Times New Roman — plus the exact Bebas glyphs
extracted from the reference. Embedding as data-URIs means Playwright needs no
network or system fonts, so output is byte-stable across machines.
"""

from __future__ import annotations

import base64
import functools
from pathlib import Path

from app.core.config import BACKEND_ROOT

_FONT_DIR = BACKEND_ROOT / "assets" / "fonts"

# Latin block carries digits, %, punctuation; Cyrillic block the alphabet.
LATIN = "U+0000-00FF,U+0131,U+0152-0153,U+2000-206F,U+2116,U+2122,U+2212"
CYR = "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116"

# (family, weight, style, filename, unicode-range|None)
_SPEC: list[tuple[str, int, str, str, str | None]] = [
    ("Bebas", 700, "normal", "bebas-ref.woff2", None),
    ("Oswald", 700, "normal", "oswald-700-latin.woff2", LATIN),
    ("Oswald", 700, "normal", "oswald-700-cyr.woff2", CYR),
    ("Lora", 400, "normal", "lora-400-latin.woff2", LATIN),
    ("Lora", 400, "normal", "lora-400-cyr.woff2", CYR),
    ("Lora", 700, "normal", "lora-700-latin.woff2", LATIN),
    ("Lora", 700, "normal", "lora-700-cyr.woff2", CYR),
    ("Tinos", 400, "normal", "tinos-400-latin.woff2", LATIN),
    ("Tinos", 400, "normal", "tinos-400-cyr.woff2", CYR),
    ("Tinos", 700, "normal", "tinos-700-latin.woff2", LATIN),
    ("Tinos", 700, "normal", "tinos-700-cyr.woff2", CYR),
    ("NotoSans", 400, "normal", "notosans-400-latin.woff2", LATIN),
    ("NotoSans", 400, "normal", "notosans-400-cyr.woff2", CYR),
    ("NotoSans", 700, "normal", "notosans-700-latin.woff2", LATIN),
    ("NotoSans", 700, "normal", "notosans-700-cyr.woff2", CYR),
    ("OpenSansIt", 400, "italic", "opensans-400i-latin.woff2", LATIN),
    ("OpenSansIt", 400, "italic", "opensans-400i-cyr.woff2", CYR),
    ("Montserrat", 700, "normal", "montserrat-700-latin.woff2", LATIN),
    ("Montserrat", 700, "normal", "montserrat-700-cyr.woff2", CYR),
]


@functools.lru_cache(maxsize=1)
def font_face_css() -> str:
    """Build the full @font-face block (cached; fonts don't change at runtime)."""
    rules: list[str] = []
    for family, weight, style, fname, urange in _SPEC:
        path = _FONT_DIR / fname
        if not path.exists():
            continue
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        ur = f"unicode-range:{urange};" if urange else ""
        rules.append(
            f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"font-style:{style};font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');{ur}}}"
        )
    return "\n".join(rules)
