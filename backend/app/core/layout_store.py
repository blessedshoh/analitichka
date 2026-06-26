"""Persistence for the Design-mode LayoutConfig (config/layout.json).

Load merges the saved file over defaults (so new fields added later get
sane defaults). Save writes the full config. Reset removes the file so the
reference defaults take over again.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.core.config import BACKEND_ROOT, get_settings
from app.models.layout import LayoutConfig


def _path() -> Path:
    custom = getattr(get_settings(), "layout_path", None)
    return Path(custom) if custom else BACKEND_ROOT / "config" / "layout.json"


def default_layout() -> LayoutConfig:
    return LayoutConfig()


def load_layout() -> LayoutConfig:
    p = _path()
    if not p.exists():
        return default_layout()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        # Merge over defaults: unknown/missing keys fall back gracefully.
        return LayoutConfig(**{**default_layout().model_dump(), **data})
    except (OSError, json.JSONDecodeError, ValueError):
        return default_layout()


def save_layout(cfg: LayoutConfig) -> LayoutConfig:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(cfg.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return cfg


def reset_layout() -> LayoutConfig:
    p = _path()
    try:
        p.unlink(missing_ok=True)
    except OSError:
        pass
    return default_layout()
