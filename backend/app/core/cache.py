"""Tiny last-known-good cache so fetchers can degrade to STALE rather than
fail. Stored as JSON files keyed by fetcher name.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from app.core.config import get_settings


def _cache_path(key: str) -> Path:
    d = Path(get_settings().cache_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{key}.json"


def save(key: str, data: dict) -> None:
    try:
        _cache_path(key).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:
        # Caching is best-effort; never let it break a fetch.
        pass


def load(key: str) -> Optional[dict]:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
