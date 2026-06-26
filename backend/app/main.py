"""FastAPI entrypoint. Run: uvicorn app.main:app --reload --port 8000"""

from __future__ import annotations

import asyncio
import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import BACKEND_ROOT, get_settings
from app.core.scheduler import run_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the optional morning auto-refresh loop, if enabled."""
    task = None
    if get_settings().scheduler_enabled:
        task = asyncio.create_task(run_scheduler())
    try:
        yield
    finally:
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task


app = FastAPI(
    title="NBU Market Review Newsletter Generator",
    version="0.1.0",
    description="Automates the recurring two-page treasury markets PDF newsletter.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# In the single-container deploy the built frontend is copied to backend/static
# and served same-origin (so the SPA's /api calls just work). Mounted last so
# it only catches paths the API router didn't. Absent in local dev (two
# services), where this falls back to the JSON root below.
_STATIC_DIR = BACKEND_ROOT / "static"
if _STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="ui")
else:
    @app.get("/")
    def root() -> dict:
        return {"service": "nbu-newsletter", "docs": "/docs", "api": "/api/health"}
