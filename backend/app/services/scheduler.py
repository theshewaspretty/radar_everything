from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.collector_service import CollectorService

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def scheduled_collect() -> None:
    logger.info("Scheduled collection started")
    db = SessionLocal()
    try:
        service = CollectorService(db)
        # depth=1 → current week / month / year only (keeps API usage modest)
        await service.collect_recent(depth=1)
        logger.info("Scheduled collection finished")
    except Exception:  # noqa: BLE001
        logger.exception("Scheduled collection failed")
    finally:
        db.close()


def start_scheduler() -> None:
    settings = get_settings()
    if scheduler.running:
        return
    hours = ",".join(str(h) for h in settings.collect_hour_list)
    scheduler.add_job(
        scheduled_collect,
        CronTrigger(hour=hours, minute=0),
        id="collect_all",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started (hours=%s UTC)", hours)


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)


async def run_startup_collect() -> None:
    settings = get_settings()
    if not settings.collect_on_startup:
        return
    # Delay slightly so API is ready
    await asyncio.sleep(2)
    await scheduled_collect()
