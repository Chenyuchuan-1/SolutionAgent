from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from app.core.config import get_settings
from tools.web_search.base import HttpSearchTool, credibility_for_url, normalize_result


class DuckDuckGoTool(HttpSearchTool):
    name = "duckduckgo_searxng"

    async def search(self, query: str, max_results: int = 5, source_type: str = "webpage", freshness: str = "any") -> list[dict[str, Any]]:
        settings = get_settings()
        if settings.searxng_endpoint:
            data = await self._get_json(settings.searxng_endpoint.rstrip("/") + "/search", params={"q": query, "format": "json", "language": "zh-CN"})
            rows = data.get("results", [])[:max_results]
            return [normalize_result(tool=self.name, query=query, title=r.get("title", ""), url=r.get("url", ""), snippet=r.get("content", ""), source_type=source_type, relevance_score=0.55, credibility_score=credibility_for_url(r.get("url", ""), source_type), freshness_score=0.45) for r in rows]
        # 免依赖兜底：返回可点击搜索页，标记需要核验，避免伪造结果。
        return [normalize_result(tool=self.name, query=query, title=f"DuckDuckGo 搜索：{query}", url=f"https://duckduckgo.com/?q={quote_plus(query)}", snippet="未配置 SearXNG，本条为可人工核验的搜索入口。", source_type=source_type, relevance_score=0.35, credibility_score=0.25, freshness_score=0.2, need_verification=True)]
