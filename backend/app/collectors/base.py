from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any, Literal


PeriodType = Literal["weekly", "monthly", "yearly"]


@dataclass
class CollectedItem:
    external_id: str
    title: str
    url: str
    score: float
    score_label: str = "stars"
    description: str = ""
    severity: str | None = None
    language: str | None = None
    owner: str | None = None
    tags: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class PeriodWindow:
    period_type: PeriodType
    period_key: str
    start: date
    end: date


def monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


def iso_week_key(d: date) -> str:
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def month_key(d: date) -> str:
    return f"{d.year}-{d.month:02d}"


def year_key(d: date) -> str:
    return str(d.year)


def build_period_window(
    period_type: PeriodType,
    ref: date | None = None,
    *,
    week_offset: int = 0,
    month_offset: int = 0,
    year_offset: int = 0,
) -> PeriodWindow:
    """Build a closed date window for weekly / monthly / yearly collection."""
    today = ref or datetime.now(timezone.utc).date()

    if period_type == "weekly":
        start = monday_of(today) - timedelta(weeks=week_offset)
        end = start + timedelta(days=6)
        return PeriodWindow("weekly", iso_week_key(start), start, end)

    if period_type == "monthly":
        y, m = today.year, today.month
        m -= month_offset
        while m <= 0:
            m += 12
            y -= 1
        start = date(y, m, 1)
        if m == 12:
            end = date(y + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(y, m + 1, 1) - timedelta(days=1)
        return PeriodWindow("monthly", month_key(start), start, end)

    y = today.year - year_offset
    start = date(y, 1, 1)
    end = date(y, 12, 31)
    return PeriodWindow("yearly", year_key(start), start, end)


def list_recent_periods(period_type: PeriodType, count: int = 12) -> list[PeriodWindow]:
    windows: list[PeriodWindow] = []
    for i in range(count):
        if period_type == "weekly":
            windows.append(build_period_window("weekly", week_offset=i))
        elif period_type == "monthly":
            windows.append(build_period_window("monthly", month_offset=i))
        else:
            windows.append(build_period_window("yearly", year_offset=i))
    return windows


class BaseCollector(ABC):
    """Plugin interface — subclass and register to add a new source."""

    source_id: str = "base"
    name: str = "Base"
    description: str = ""
    supports_periods: tuple[PeriodType, ...] = ("weekly", "monthly", "yearly")
    supports_severity: bool = False

    @abstractmethod
    async def collect(self, window: PeriodWindow, limit: int = 30) -> list[CollectedItem]:
        raise NotImplementedError

    def to_meta(self) -> dict[str, Any]:
        return {
            "id": self.source_id,
            "name": self.name,
            "description": self.description,
            "supports_periods": list(self.supports_periods),
            "supports_severity": self.supports_severity,
        }
