from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.schemas import CollectRequest, HealthResponse
from app.collectors.base import PeriodType
from app.collectors.registry import list_collectors
from app.core.config import get_settings
from app.core.database import SessionLocal, get_db
from app.services.collector_service import CollectorService
from app.services.query_service import QueryService

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        sources=[c.source_id for c in list_collectors()],
    )


@router.get("/sources")
def sources(db: Session = Depends(get_db)):
    return {"sources": QueryService(db).list_sources()}


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return QueryService(db).stats()


@router.get("/periods/{source}/{period_type}")
def periods(
    source: str,
    period_type: PeriodType,
    depth: int = Query(default=16, ge=1, le=52),
    db: Session = Depends(get_db),
):
    return {"source": source, "period_type": period_type, "periods": QueryService(db).list_periods(source, period_type, depth)}


@router.get("/trends/{source}")
def trends(
    source: str,
    period_type: PeriodType = Query(default="weekly"),
    period_key: str | None = None,
    limit: int = Query(default=30, ge=1, le=100),
    severity: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    return QueryService(db).get_trends(
        source,
        period_type,
        period_key,
        limit=limit,
        severity=severity,
        q=q,
    )


@router.get("/runs")
def runs(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return {"runs": QueryService(db).recent_runs(limit)}


async def _run_collect(payload: CollectRequest) -> None:
    db = SessionLocal()
    try:
        service = CollectorService(db)
        if payload.source and payload.period_type and payload.period_key:
            await service.collect_one(
                payload.source,
                payload.period_type,
                period_key=payload.period_key,
                limit=payload.limit,
            )
        elif payload.source and payload.period_type:
            await service.collect_one(payload.source, payload.period_type, limit=payload.limit)
        else:
            await service.collect_recent(
                source_id=payload.source,
                period_type=payload.period_type,
                depth=payload.depth,
            )
    finally:
        db.close()


@router.post("/collect")
async def collect(payload: CollectRequest, background: BackgroundTasks, sync: bool = Query(default=False)):
    settings = get_settings()
    if payload.source and payload.source not in settings.enabled_source_list:
        # still allow if registered
        if not any(c.source_id == payload.source for c in list_collectors()):
            raise HTTPException(status_code=404, detail=f"Unknown source: {payload.source}")

    if sync:
        db = SessionLocal()
        try:
            service = CollectorService(db)
            if payload.source and payload.period_type:
                run = await service.collect_one(
                    payload.source,
                    payload.period_type,
                    period_key=payload.period_key,
                    limit=payload.limit,
                )
                return {
                    "mode": "sync",
                    "run": {
                        "id": run.id,
                        "status": run.status,
                        "item_count": run.item_count,
                        "message": run.message,
                        "period_key": run.period_key,
                    },
                }
            runs = await service.collect_recent(payload.source, payload.period_type, depth=payload.depth)
            return {
                "mode": "sync",
                "runs": [{"id": r.id, "status": r.status, "item_count": r.item_count, "period_key": r.period_key} for r in runs],
            }
        finally:
            db.close()

    background.add_task(_run_collect, payload)
    return {"mode": "async", "status": "started", "request": payload.model_dump()}
