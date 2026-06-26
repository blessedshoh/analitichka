"""Optional morning auto-refresh.

A tiny asyncio loop that, once a day at `refresh_hour`, pre-warms the CBU
rate cache so the form opens already populated. No external scheduler
dependency. Enabled via `SCHEDULER_ENABLED=true`. Failures are swallowed so a
bad fetch never takes the service down.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

from app.core.config import get_settings


def _seconds_until(hour: int) -> float:
    now = datetime.now()
    target = now.replace(hour=hour % 24, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def _refresh_once() -> None:
    # Imported lazily to avoid import cycles at module load.
    from app.fetchers import cbu_currency

    try:
        await asyncio.to_thread(cbu_currency.fetch)  # populates last-known cache
    except Exception:  # noqa: BLE001 - never crash the loop
        pass


async def run_scheduler() -> None:
    settings = get_settings()
    # Warm once on boot so the very first morning is covered too.
    await _refresh_once()
    while True:
        await asyncio.sleep(_seconds_until(settings.refresh_hour))
        await _refresh_once()
