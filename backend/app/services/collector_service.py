from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.collectors.base import PeriodType, PeriodWindow, build_period_window, list_recent_periods
from app.collectors.github import collect_github_with_fallback
from app.collectors.registry import get_collector, list_collectors
from app.core.config import get_settings
from app.models.entities import CollectRun, SourceMeta, TrendItem

logger = logging.getLogger(__name__)


class CollectorService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def ensure_source_meta(self) -> None:
        for collector in list_collectors():
            existing = self.db.scalar(select(SourceMeta).where(SourceMeta.source_id == collector.source_id))
            if existing:
                existing.name = collector.name
                existing.description = collector.description
                existing.enabled = 1 if collector.source_id in self.settings.enabled_source_list else 0
            else:
                self.db.add(
                    SourceMeta(
                        source_id=collector.source_id,
                        name=collector.name,
                        description=collector.description,
                        enabled=1 if collector.source_id in self.settings.enabled_source_list else 0,
                    )
                )
        self.db.commit()

    async def collect_one(
        self,
        source_id: str,
        period_type: PeriodType,
        *,
        week_offset: int = 0,
        month_offset: int = 0,
        year_offset: int = 0,
        limit: int | None = None,
        period_key: str | None = None,
    ) -> CollectRun:
        collector = get_collector(source_id)
        if not collector:
            raise ValueError(f"Unknown source: {source_id}")

        if period_key:
            window = self._window_from_key(period_type, period_key)
        else:
            window = build_period_window(
                period_type,
                week_offset=week_offset,
                month_offset=month_offset,
                year_offset=year_offset,
            )

        run = CollectRun(
            source=source_id,
            period_type=period_type,
            period_key=window.period_key,
            status="running",
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        limit = limit or self.settings.default_limit
        try:
            if source_id == "github":
                items = await collect_github_with_fallback(window, limit=limit)
            else:
                items = await collector.collect(window, limit=limit)

            self.db.execute(
                delete(TrendItem).where(
                    TrendItem.source == source_id,
                    TrendItem.period_type == period_type,
                    TrendItem.period_key == window.period_key,
                )
            )

            for rank, item in enumerate(items, start=1):
                self.db.add(
                    TrendItem(
                        source=source_id,
                        external_id=item.external_id,
                        title=item.title,
                        description=item.description,
                        url=item.url,
                        score=item.score,
                        score_label=item.score_label,
                        severity=item.severity,
                        language=item.language,
                        owner=item.owner,
                        tags=",".join(item.tags),
                        extra_json=json.dumps(item.extra, ensure_ascii=False),
                        period_type=period_type,
                        period_key=window.period_key,
                        rank=rank,
                        collected_at=datetime.now(timezone.utc),
                    )
                )

            run.status = "success"
            run.item_count = len(items)
            run.message = f"Collected {len(items)} items"
            run.finished_at = datetime.now(timezone.utc)

            meta = self.db.scalar(select(SourceMeta).where(SourceMeta.source_id == source_id))
            if meta:
                meta.last_collected_at = run.finished_at

            self.db.commit()
            self.db.refresh(run)
            return run
        except Exception as exc:  # noqa: BLE001
            logger.exception("Collect failed for %s/%s: %s", source_id, window.period_key, exc)
            run.status = "failed"
            run.message = str(exc)[:1000]
            run.finished_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(run)
            return run

    async def collect_recent(
        self,
        source_id: str | None = None,
        period_type: PeriodType | None = None,
        depth: int = 4,
    ) -> list[CollectRun]:
        sources = [source_id] if source_id else self.settings.enabled_source_list
        periods: list[PeriodType] = [period_type] if period_type else ["weekly", "monthly", "yearly"]
        runs: list[CollectRun] = []

        for sid in sources:
            for ptype in periods:
                windows = list_recent_periods(ptype, count=depth if ptype != "yearly" else min(depth, 3))
                for window in windows:
                    run = await self.collect_one(sid, ptype, period_key=window.period_key)
                    runs.append(run)
        return runs

    def _window_from_key(self, period_type: PeriodType, period_key: str) -> PeriodWindow:
        from datetime import date, timedelta

        if period_type == "weekly":
            # 2026-W47
            year_s, week_s = period_key.split("-W")
            year, week = int(year_s), int(week_s)
            start = date.fromisocalendar(year, week, 1)
            end = start + timedelta(days=6)
            return PeriodWindow("weekly", period_key, start, end)
        if period_type == "monthly":
            year_s, month_s = period_key.split("-")
            year, month = int(year_s), int(month_s)
            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(year, month + 1, 1) - timedelta(days=1)
            return PeriodWindow("monthly", period_key, start, end)
        year = int(period_key)
        return PeriodWindow("yearly", period_key, date(year, 1, 1), date(year, 12, 31))
