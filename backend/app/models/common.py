"""Shared model primitives used across every fetcher result."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class FetchStatus(str, Enum):
    """How a fetcher fared. Never raise — degrade and flag instead."""

    OK = "ok"
    STALE = "stale"          # served last-known / cached values
    EMPTY = "empty"          # nothing available, manual entry required
    ERROR = "error"          # the fetch failed, see `warning`
    MANUAL = "manual"        # value was typed/edited by a human


class SourceMeta(BaseModel):
    """Provenance + health attached to every fetched table.

    The frontend reads `status` and `warning` to decide whether to show a
    yellow "needs review" banner. Nothing is ever silently auto-filled.
    """

    source: str = Field(..., description="Human label, e.g. 'cbu.uz JSON'")
    status: FetchStatus = FetchStatus.OK
    warning: Optional[str] = Field(
        default=None,
        description="Set when degraded so the UI can flag the section.",
    )
    fetched_at: Optional[str] = Field(
        default=None, description="ISO timestamp of the fetch."
    )


class ValueCell(BaseModel):
    """A single editable numeric cell with an optional validation flag.

    `flagged` drives the highlighted-row UX (e.g. when a Claude-extracted
    percent disagrees with the server-recomputed one).
    """

    value: Optional[float] = None
    flagged: bool = False
    note: Optional[str] = None
