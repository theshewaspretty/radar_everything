"""Example plugin — copy this file and register in registry.py to add a source.

from app.collectors.example_plugin import ExampleCollector
register(ExampleCollector())
"""

from __future__ import annotations

from app.collectors.base import BaseCollector, CollectedItem, PeriodWindow


class ExampleCollector(BaseCollector):
    source_id = "example"
    name = "Example Source"
    description = "새 소스를 추가할 때 참고하는 템플릿 컬렉터"
    supports_periods = ("weekly", "monthly", "yearly")

    async def collect(self, window: PeriodWindow, limit: int = 30) -> list[CollectedItem]:
        return [
            CollectedItem(
                external_id=f"example-{window.period_key}",
                title=f"Example signal ({window.period_key})",
                description=f"Window {window.start} → {window.end}",
                url="https://example.com",
                score=42,
                score_label="likes",
                tags=["example", window.period_type],
            )
        ][:limit]
