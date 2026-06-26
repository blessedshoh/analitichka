"""Central configuration. Everything secret or deployment-specific lives in
env vars / config files — never hardcoded. See `.env.example`.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/  (this file is backend/app/core/config.py)
BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Brand / design -----------------------------------------------------
    # Single source of truth for the gold accent. The template reads this via
    # the API so the colour is defined in exactly one place.
    accent_gold: str = "#f4e7d4"
    page_bg: str = "#faf4ea"  # parchment/cream base under the watermark

    # Background asset: a file PATH so staff can swap the (transparent) PNG
    # without touching code. Placement is a single switch.
    background_asset: str = str(BACKEND_ROOT / "assets" / "background.png")
    # one of: "watermark" | "cover" | "header" | "none"
    background_placement: str = "watermark"
    background_opacity: float = 0.07
    logo_asset: str = str(BACKEND_ROOT / "assets" / "nbu_logo.png")

    # --- Data sources -------------------------------------------------------
    cbu_json_url: str = "https://cbu.uz/ru/arkhiv-kursov-valyut/json/"
    cbu_base_url: str = "https://cbu.uz"
    bloomberg_map_path: str = str(BACKEND_ROOT / "config" / "bloomberg_map.yaml")

    # CBU rates we surface in the local FX table (UZS per unit).
    cbu_currencies: list[str] = ["USD", "EUR", "RUB", "CNY", "GBP"]

    # --- Telegram (MTProto) -------------------------------------------------
    telegram_api_id: Optional[int] = None
    telegram_api_hash: Optional[str] = None
    telegram_session: str = str(BACKEND_ROOT / "config" / "tg.session")
    telegram_stock_channel: str = ""   # @channel or numeric id
    telegram_news_channels: list[str] = []

    # --- Anthropic ----------------------------------------------------------
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-sonnet-4-6"

    # --- Validation ---------------------------------------------------------
    # Tolerance (percentage points) for stock change_pct recompute mismatch.
    change_pct_tolerance: float = 0.05

    # --- Cache --------------------------------------------------------------
    cache_dir: str = str(BACKEND_ROOT / ".cache")

    # --- Misc ---------------------------------------------------------------
    http_timeout: float = 15.0
    cors_origins: list[str] = ["http://localhost:3000"]

    # Optional explicit Chromium path for Playwright. Leave empty to use the
    # browser installed by `playwright install chromium`. Set this when the
    # environment ships a pre-installed Chromium at a fixed location.
    playwright_executable_path: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
