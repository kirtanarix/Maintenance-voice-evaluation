"""Strict Pydantic schema for the five Gemini extraction parameters."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceExtraction(BaseModel):
    """Exactly five top-level fields; no extras allowed."""

    model_config = ConfigDict(extra="forbid")

    assets: str | list[str] | None = Field(
        ...,
        description="Equipment or assets explicitly mentioned; null if none.",
    )
    quantities: list[str] | None = Field(
        ...,
        description="Explicit quantities with specs when spoken; null if none.",
    )
    hours: list[str | dict[str, Any]] | None = Field(
        ...,
        description=(
            "Explicit time durations; preserve work vs downtime separately; null if none."
        ),
    )
    dates: str | list[str] | None = Field(
        ...,
        description="Scheduling phrases as spoken; null if none.",
    )
    approval_intent: str | None = Field(
        ...,
        description="Explicit approval or permission intent; null if not mentioned.",
    )
