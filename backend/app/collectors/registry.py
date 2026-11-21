from __future__ import annotations

from typing import Type

from app.collectors.base import BaseCollector
from app.collectors.github import GitHubCollector
from app.collectors.mcp import MCPCollector
from app.collectors.vulnerability import VulnerabilityCollector

# ---------------------------------------------------------------------------
# Plugin registry — add a new source by registering a BaseCollector subclass.
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, BaseCollector] = {}


def register(collector: BaseCollector) -> BaseCollector:
    _REGISTRY[collector.source_id] = collector
    return collector


def register_class(cls: Type[BaseCollector]) -> Type[BaseCollector]:
    register(cls())
    return cls


def get_collector(source_id: str) -> BaseCollector | None:
    return _REGISTRY.get(source_id)


def list_collectors(enabled_only: list[str] | None = None) -> list[BaseCollector]:
    collectors = list(_REGISTRY.values())
    if enabled_only is not None:
        allowed = set(enabled_only)
        collectors = [c for c in collectors if c.source_id in allowed]
    return collectors


def bootstrap_default_collectors() -> None:
    """Idempotent registration of built-in sources."""
    if _REGISTRY:
        return
    register(GitHubCollector())
    register(MCPCollector())
    register(VulnerabilityCollector())
