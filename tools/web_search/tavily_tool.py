from __future__ import annotations

from typing import Any

from app.core.config import get_settings
from tools.web_search.base import HttpSearchTool, credibility_for_url, normalize_result


class TavilyTool(HttpSearchTool):
    name = "tavily"

    async def search(self, query: str, max_results: int = 5, source_type: str = "webpage", freshness: str = "any") -> list[dict[str, Any]]:
        settings = get_settings()
        if not settings.tavily_api_key:
            return []
        payload = {"api_key": settings.tavily_api_key, "query": query, "max_results": max_results, "include_answer": True, "include_raw_content": False}
        data = await self._post_json("https://api.tavily.com/search", json_data=payload)
        results = []
        for item in data.get("results", [])[:max_results]:
            url = item.get("url", "")
            results.append(normalize_result(tool=self.name, query=query, title=item.get("title", ""), url=url, snippet=item.get("content", ""), source_type=source_type, relevance_score=item.get("score", 0.65), credibility_score=credibility_for_url(url, source_type), freshness_score=0.6))
        return results
