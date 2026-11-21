from __future__ import annotations

import json
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.collectors.base import PeriodType, list_recent_periods
from app.collectors.registry import list_collectors
from app.models.entities import CollectRun, SourceMeta, TrendItem


class QueryService:
    def __init__(self, db: Session):
        self.db = db

    def list_sources(self) -> list[dict[str, Any]]:
        metas = {m.source_id: m for m in self.db.scalars(select(SourceMeta)).all()}
        result = []
        for collector in list_collectors():
            meta = metas.get(collector.source_id)
            payload = collector.to_meta()
            payload["enabled"] = bool(meta.enabled) if meta else True
            payload["last_collected_at"] = meta.last_collected_at.isoformat() if meta and meta.last_collected_at else None
            result.append(payload)
        return result

    def list_periods(self, source: str, period_type: PeriodType, depth: int = 16) -> list[dict[str, Any]]:
        windows = list_recent_periods(period_type, count=depth)
        existing = set(
            self.db.scalars(
                select(TrendItem.period_key)
                .where(TrendItem.source == source, TrendItem.period_type == period_type)
                .distinct()
            ).all()
        )
        # Also include any stored keys not in the recent window list
        stored = [
            {"period_key": k, "has_data": True, "start": None, "end": None}
            for k in existing
            if k not in {w.period_key for w in windows}
        ]
        out = [
            {
                "period_key": w.period_key,
                "has_data": w.period_key in existing,
                "start": w.start.isoformat(),
                "end": w.end.isoformat(),
            }
            for w in windows
        ]
        return out + stored

    def get_trends(
        self,
        source: str,
        period_type: PeriodType,
        period_key: str | None = None,
        *,
        limit: int = 30,
        severity: str | None = None,
        q: str | None = None,
    ) -> dict[str, Any]:
        if not period_key:
            # latest period with data, else current window key
            latest = self.db.scalar(
                select(TrendItem.period_key)
                .where(TrendItem.source == source, TrendItem.period_type == period_type)
                .order_by(desc(TrendItem.collected_at))
                .limit(1)
            )
            period_key = latest or list_recent_periods(period_type, 1)[0].period_key

        stmt = select(TrendItem).where(
            TrendItem.source == source,
            TrendItem.period_type == period_type,
            TrendItem.period_key == period_key,
        )
        if severity:
            stmt = stmt.where(func.lower(TrendItem.severity) == severity.lower())
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                (TrendItem.title.ilike(like))
                | (TrendItem.description.ilike(like))
                | (TrendItem.tags.ilike(like))
            )
        stmt = stmt.order_by(TrendItem.rank.asc(), desc(TrendItem.score)).limit(limit)
        rows = self.db.scalars(stmt).all()
        return {
            "source": source,
            "period_type": period_type,
            "period_key": period_key,
            "count": len(rows),
            "items": [self._serialize_item(r) for r in rows],
        }

    def recent_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.db.scalars(select(CollectRun).order_by(desc(CollectRun.started_at)).limit(limit)).all()
        return [
            {
                "id": r.id,
                "source": r.source,
                "period_type": r.period_type,
                "period_key": r.period_key,
                "status": r.status,
                "item_count": r.item_count,
                "message": r.message,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            }
            for r in rows
        ]

    def stats(self) -> dict[str, Any]:
        total = self.db.scalar(select(func.count()).select_from(TrendItem)) or 0
        by_source = dict(
            self.db.execute(
                select(TrendItem.source, func.count()).group_by(TrendItem.source)
            ).all()
        )
        last_run = self.db.scalar(select(CollectRun).order_by(desc(CollectRun.started_at)).limit(1))
        return {
            "total_items": total,
            "by_source": by_source,
            "last_run": {
                "source": last_run.source,
                "status": last_run.status,
                "started_at": last_run.started_at.isoformat() if last_run and last_run.started_at else None,
            }
            if last_run
            else None,
        }

    @staticmethod
    def _serialize_item(row: TrendItem) -> dict[str, Any]:
        try:
            extra = json.loads(row.extra_json or "{}")
        except json.JSONDecodeError:
            extra = {}
        return {
            "id": row.id,
            "source": row.source,
            "external_id": row.external_id,
            "title": row.title,
            "description": row.description,
            "url": row.url,
            "score": row.score,
            "score_label": row.score_label,
            "severity": row.severity,
            "language": row.language,
            "owner": row.owner,
            "tags": [t for t in (row.tags or "").split(",") if t],
            "extra": extra,
            "period_type": row.period_type,
            "period_key": row.period_key,
            "rank": row.rank,
            "collected_at": row.collected_at.isoformat() if row.collected_at else None,
        }
