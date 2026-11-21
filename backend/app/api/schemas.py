from typing import Any, Literal

from pydantic import BaseModel, Field


PeriodType = Literal["weekly", "monthly", "yearly"]


class CollectRequest(BaseModel):
    source: str | None = Field(default=None, description="github | mcp | vulnerability | omit for all")
    period_type: PeriodType | None = None
    period_key: str | None = None
    depth: int = Field(default=2, ge=1, le=12)
    limit: int = Field(default=30, ge=1, le=100)


class HealthResponse(BaseModel):
    status: str
    version: str
    sources: list[str]
