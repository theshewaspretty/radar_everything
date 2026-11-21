from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.collectors.base import BaseCollector, CollectedItem, PeriodWindow
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MCPCollector(BaseCollector):
    """Popular MCP servers ranked by GitHub stars + official registry metadata."""

    source_id = "mcp"
    name = "MCP Servers"
    description = "Model Context Protocol 서버 — GitHub star / registry 기준 인기 순위"
    supports_periods = ("weekly", "monthly", "yearly")

    GITHUB_SEARCH = "https://api.github.com/search/repositories"
    REGISTRY = "https://registry.modelcontextprotocol.io/v0.1/servers"

    def _headers(self) -> dict[str, str]:
        settings = get_settings()
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "radar-everything/1.0",
        }
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        return headers

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    async def _github_search(self, query: str, per_page: int) -> list[dict[str, Any]]:
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": per_page}
        async with httpx.AsyncClient(timeout=40.0) as client:
            resp = await client.get(self.GITHUB_SEARCH, params=params, headers=self._headers())
            resp.raise_for_status()
            return resp.json().get("items", [])

    async def _registry_sample(self, limit: int = 50) -> list[dict[str, Any]]:
        servers: list[dict[str, Any]] = []
        cursor: str | None = None
        async with httpx.AsyncClient(timeout=40.0) as client:
            while len(servers) < limit:
                params: dict[str, Any] = {"limit": min(100, limit), "version": "latest"}
                if cursor:
                    params["cursor"] = cursor
                try:
                    resp = await client.get(self.REGISTRY, params=params)
                    resp.raise_for_status()
                    payload = resp.json()
                except Exception as exc:  # noqa: BLE001
                    logger.warning("MCP registry fetch failed: %s", exc)
                    break
                batch = payload.get("servers") or []
                servers.extend(batch)
                cursor = (payload.get("metadata") or {}).get("nextCursor")
                if not cursor or not batch:
                    break
        return servers[:limit]

    def _repo_from_registry(self, entry: dict[str, Any]) -> str | None:
        server = entry.get("server") if isinstance(entry.get("server"), dict) else entry
        if not isinstance(server, dict):
            return None
        # Prefer repository URL fields when present
        for key in ("repository", "repo", "homepage", "websiteUrl"):
            val = server.get(key)
            if isinstance(val, dict):
                url = val.get("url") or val.get("uri")
            else:
                url = val
            if isinstance(url, str) and "github.com/" in url:
                path = url.split("github.com/", 1)[1].strip("/").removesuffix(".git")
                parts = path.split("/")
                if len(parts) >= 2:
                    return f"{parts[0]}/{parts[1]}"
        name = server.get("name") or entry.get("name")
        if isinstance(name, str) and "/" in name and not name.startswith("io."):
            return name
        return None

    async def collect(self, window: PeriodWindow, limit: int = 30) -> list[CollectedItem]:
        start = window.start.isoformat()
        end = window.end.isoformat()

        queries = [
            f'topic:mcp-server created:{start}..{end} stars:>1',
            f'topic:mcp created:{start}..{end} stars:>5',
            f'"model context protocol" created:{start}..{end} stars:>5',
            # Broader evergreen ranking for yearly / sparse weeks
            "topic:mcp-server stars:>20",
            "topic:mcp stars:>50",
        ]

        seen: set[str] = set()
        items: list[CollectedItem] = []

        for query in queries:
            try:
                raw = await self._github_search(query, min(limit, 40))
            except Exception as exc:  # noqa: BLE001
                logger.exception("MCP GitHub search failed (%s): %s", query, exc)
                continue

            for repo in raw:
                full_name = repo.get("full_name") or ""
                if not full_name or full_name in seen:
                    continue
                # Soft period filter for evergreen queries: prefer created/pushed in window
                created = (repo.get("created_at") or "")[:10]
                pushed = (repo.get("pushed_at") or "")[:10]
                if "created:" not in query:
                    in_window = (start <= created <= end) or (start <= pushed <= end)
                    if window.period_type != "yearly" and not in_window and len(items) >= limit:
                        continue

                seen.add(full_name)
                topics = repo.get("topics") or []
                items.append(
                    CollectedItem(
                        external_id=str(repo.get("id") or full_name),
                        title=full_name,
                        description=(repo.get("description") or "")[:800],
                        url=repo.get("html_url") or f"https://github.com/{full_name}",
                        score=float(repo.get("stargazers_count") or 0),
                        score_label="stars",
                        language=repo.get("language"),
                        owner=(repo.get("owner") or {}).get("login"),
                        tags=["mcp", *list(topics)[:10]],
                        extra={
                            "forks": repo.get("forks_count"),
                            "created_at": repo.get("created_at"),
                            "pushed_at": repo.get("pushed_at"),
                            "query": query,
                        },
                    )
                )
            if len(items) >= limit:
                break

        # Enrich / fill from official registry when GitHub results are thin
        if len(items) < max(8, limit // 2):
            registry = await self._registry_sample(limit=80)
            for entry in registry:
                repo_name = self._repo_from_registry(entry)
                server = entry.get("server") if isinstance(entry.get("server"), dict) else entry
                name = (server or {}).get("name") if isinstance(server, dict) else None
                title = repo_name or name or "unknown-mcp"
                if title in seen:
                    continue
                seen.add(title)
                desc = ""
                if isinstance(server, dict):
                    desc = (server.get("description") or "")[:800]
                url = f"https://github.com/{repo_name}" if repo_name else f"https://registry.modelcontextprotocol.io"
                items.append(
                    CollectedItem(
                        external_id=quote(str(title)),
                        title=str(title),
                        description=desc or "Official MCP registry entry",
                        url=url,
                        score=0.0,
                        score_label="registry",
                        tags=["mcp", "registry"],
                        extra={"registry": True},
                    )
                )
                if len(items) >= limit:
                    break

        items.sort(key=lambda x: x.score, reverse=True)
        return items[:limit]
