"""HTTP API. Thin layer over fetchers + renderer.

Every fetch endpoint returns the pydantic model directly (with its meta /
warning) so the frontend can show it in editable grids and flag degraded
sources. Generation takes the fully-reviewed Newsletter back and renders.
"""

from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import HTMLResponse, Response

from app.core.config import get_settings
from app.fetchers import (
    bloomberg_excel,
    cbu_currency,
    cbu_money_market,
    telegram_news,
    telegram_stocks,
)
from app.models.bloomberg import BloombergData
from app.models.fx import CbuFxTable
from app.models.money_market import MoneyMarketLocal
from app.models.newsletter import Newsletter
from app.models.stocks import StockTable
from app import sample_data
from app.rendering import pdf as pdf_renderer

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/config")
def config() -> dict:
    """Design tokens the frontend mirrors (single source of truth)."""
    s = get_settings()
    return {
        "accent_gold": s.accent_gold,
        "page_bg": s.page_bg,
        "background_placement": s.background_placement,
        "cbu_currencies": s.cbu_currencies,
    }


@router.get("/sample", response_model=Newsletter)
def sample() -> Newsletter:
    """Reference-issue payload to pre-fill the form."""
    return sample_data.sample_newsletter()


# --------------------------------------------------------------------------- #
# Fetchers
# --------------------------------------------------------------------------- #
@router.post("/fetch/cbu-currency", response_model=CbuFxTable)
def fetch_cbu_currency(on_date: Optional[str] = None) -> CbuFxTable:
    d = date.fromisoformat(on_date) if on_date else None
    return cbu_currency.fetch(on_date=d)


@router.post("/fetch/money-market", response_model=MoneyMarketLocal)
def fetch_money_market() -> MoneyMarketLocal:
    return cbu_money_market.fetch()


@router.post("/upload/bloomberg", response_model=BloombergData)
async def upload_bloomberg(file: UploadFile = File(...)) -> BloombergData:
    suffix = Path(file.filename or "upload.xlsx").suffix or ".xlsx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        return bloomberg_excel.parse(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/fetch/stocks", response_model=StockTable)
async def fetch_stocks() -> StockTable:
    """Telegram image -> Claude extraction -> validated grid."""
    return await telegram_stocks.fetch()


@router.post("/upload/stock-image", response_model=StockTable)
async def upload_stock_image(file: UploadFile = File(...)) -> StockTable:
    """Manual fallback: upload the stock-results photo directly."""
    suffix = Path(file.filename or "img.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        return telegram_stocks.extract_from_path(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/news/drafts")
async def news_drafts() -> dict:
    return await telegram_news.fetch_news_drafts()


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
@router.post("/preview", response_class=HTMLResponse)
def preview(data: Newsletter) -> HTMLResponse:
    """Live HTML preview for the frontend iframe (no Chromium needed)."""
    return HTMLResponse(pdf_renderer.render_html(data))


@router.post("/generate")
async def generate(data: Newsletter) -> Response:
    pdf_bytes = await pdf_renderer.render_pdf(data)
    issue = data.meta.issue_date or "issue"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="nbu-review-{issue}.pdf"'
        },
    )
