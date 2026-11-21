from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "radar_everything"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = "sqlite:///./data/radar_everything.db"
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080"

    github_token: str = ""
    github_per_page: int = 30
    nvd_api_key: str = ""

    collect_on_startup: bool = True
    collect_cron_hours: str = "6,18"
    enabled_sources: str = "github,mcp,vulnerability"
    default_limit: int = 30

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def enabled_source_list(self) -> list[str]:
        return [s.strip() for s in self.enabled_sources.split(",") if s.strip()]

    @property
    def collect_hour_list(self) -> list[int]:
        hours: list[int] = []
        for part in self.collect_cron_hours.split(","):
            part = part.strip()
            if part.isdigit():
                hours.append(int(part))
        return hours or [6, 18]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.database_url.startswith("sqlite:///"):
        db_path = settings.database_url.removeprefix("sqlite:///")
        # Absolute URLs use sqlite:////abs/path → path starts with /
        Path(db_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    return settings
