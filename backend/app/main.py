from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.collectors.registry import bootstrap_default_collectors
from app.core.config import get_settings
from app.core.database import SessionLocal, init_db
from app.services.collector_service import CollectorService
from app.services.scheduler import run_startup_collect, start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("radar_everything")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    bootstrap_default_collectors()
    init_db()
    db = SessionLocal()
    try:
        CollectorService(db).ensure_source_meta()
    finally:
        db.close()

    start_scheduler()
    task = asyncio.create_task(run_startup_collect())
    logger.info("%s v%s ready", settings.app_name, settings.app_version)
    yield
    task.cancel()
    stop_scheduler()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list + ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api")

    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():
        app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

        @app.get("/")
        async def spa_index():
            return FileResponse(static_dir / "index.html")

        @app.get("/{full_path:path}")
        async def spa_fallback(full_path: str):
            candidate = static_dir / full_path
            if candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(static_dir / "index.html")

    return app


app = create_app()
