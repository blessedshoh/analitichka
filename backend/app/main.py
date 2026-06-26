"""FastAPI entrypoint. Run: uvicorn app.main:app --reload --port 8000"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings

app = FastAPI(
    title="NBU Market Review Newsletter Generator",
    version="0.1.0",
    description="Automates the recurring two-page treasury markets PDF newsletter.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root() -> dict:
    return {"service": "nbu-newsletter", "docs": "/docs", "api": "/api/health"}
