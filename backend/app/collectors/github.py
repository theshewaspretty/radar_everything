from __future__ import annotations

import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.collectors.base import BaseCollector, CollectedItem, PeriodWindow
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class GitHubCollector(BaseCollector):
    """Rank GitHub repositories by stars within a created-date window."""

    source_id = "github"
    name = "GitHub"
    description = "주간·월간·연간 기간에 생성되어 스타를 많이 받은 공개 저장소"
    supports_periods = ("weekly", "monthly", "yearly")

    API = "https://api.github.com/search/repositories"

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
    async def _search(self, query: str, per_page: int) -> list[dict]:
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": per_page}
        async with httpx.AsyncClient(timeout=40.0) as client:
            resp = await client.get(self.API, params=params, headers=self._headers())
            if resp.status_code == 403:
                logger.warning("GitHub API rate limited; retrying with fallback query may help")
            resp.raise_for_status()
            return resp.json().get("items", [])

    async def collect(self, window: PeriodWindow, limit: int = 30) -> list[CollectedItem]:
        # Inclusive GitHub search dates: created:YYYY-MM-DD..YYYY-MM-DD
        start = window.start.isoformat()
        end = window.end.isoformat()
        queries = [
            f"created:{start}..{end} stars:>5",
            f"pushed:{start}..{end} stars:>50",
        ]

        seen: set[str] = set()
        items: list[CollectedItem] = []

        for query in queries:
            try:
                raw = await self._search(query, min(limit, 50))
            except Exception as exc:  # noqa: BLE001
                logger.exception("GitHub collect failed for query=%s: %s", query, exc)
                continue

            for repo in raw:
                full_name = repo.get("full_name") or ""
                if not full_name or full_name in seen:
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
                        tags=list(topics)[:12],
                        extra={
                            "forks": repo.get("forks_count"),
                            "watchers": repo.get("watchers_count"),
                            "open_issues": repo.get("open_issues_count"),
                            "created_at": repo.get("created_at"),
                            "pushed_at": repo.get("pushed_at"),
                            "license": (repo.get("license") or {}).get("spdx_id"),
                        },
                    )
                )

        items.sort(key=lambda x: x.score, reverse=True)
        return items[:limit]


class GitHubTrendingFallback:
    """Optional HTML trending scrape used when Search API is empty/rate-limited."""

    URL = "https://github.com/trending"

    @staticmethod
    async def fetch(since: str = "weekly", limit: int = 25) -> list[CollectedItem]:
        from bs4 import BeautifulSoup

        params = {"since": since}
        headers = {"User-Agent": "radar-everything/1.0"}
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(GitHubTrendingFallback.URL, params=params, headers=headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        items: list[CollectedItem] = []
        for article in soup.select("article.Box-row")[:limit]:
            a = article.select_one("h2 a")
            if not a:
                continue
            href = (a.get("href") or "").strip()
            full_name = href.strip("/")
            desc_el = article.select_one("p")
            lang_el = article.select_one('[itemprop="programmingLanguage"]')
            star_el = article.select_one("a[href$='/stargazers']")
            stars_text = (star_el.get_text(strip=True) if star_el else "0").replace(",", "")
            try:
                stars = float(stars_text)
            except ValueError:
                stars = 0.0
            items.append(
                CollectedItem(
                    external_id=full_name,
                    title=full_name,
                    description=(desc_el.get_text(" ", strip=True) if desc_el else "")[:800],
                    url=f"https://github.com/{full_name}",
                    score=stars,
                    score_label="stars",
                    language=lang_el.get_text(strip=True) if lang_el else None,
                    owner=full_name.split("/")[0] if "/" in full_name else None,
                    tags=["trending"],
                    extra={"source": "github_trending_html", "since": since},
                )
            )
        return items


async def collect_github_with_fallback(window: PeriodWindow, limit: int = 30) -> list[CollectedItem]:
    collector = GitHubCollector()
    items = await collector.collect(window, limit=limit)
    if items:
        return items

    since_map = {"weekly": "weekly", "monthly": "monthly", "yearly": "monthly"}
    since = since_map.get(window.period_type, "weekly")
    logger.warning("GitHub Search empty for %s — using trending HTML fallback (%s)", window.period_key, since)
    try:
        return await GitHubTrendingFallback.fetch(since=since, limit=limit)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Trending fallback failed: %s", exc)
        return []
