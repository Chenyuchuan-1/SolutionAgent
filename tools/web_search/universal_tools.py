from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from app.core.config import get_settings
from tools.web_search.base import HttpSearchTool, credibility_for_url, normalize_result


class ExaTool(HttpSearchTool):
    name = "exa"

    async def search(self, query: str, max_results: int = 5, source_type: str = "webpage", freshness: str = "any") -> list[dict[str, Any]]:
        settings = get_settings()
        if not settings.exa_api_key:
            return []
        requested_results = max(1, min(max_results or settings.exa_num_results, settings.exa_num_results, 100))
        payload: dict[str, Any] = {
            "query": query,
            "type": settings.exa_search_type or "auto",
            "numResults": requested_results,
            "contents": self._contents_payload(settings.exa_content_mode, freshness),
        }
        category = self._category_for_source_type(source_type)
        if category:
            payload["category"] = category
        data = await self._post_json("https://api.exa.ai/search", headers={"x-api-key": settings.exa_api_key}, json_data=payload)
        return [self._normalize_exa_result(query, item, source_type) for item in data.get("results", [])[:requested_results]]

    def _contents_payload(self, mode: str, freshness: str) -> dict[str, Any]:
        contents: dict[str, Any] = {"highlights": True}
        if mode == "text":
            contents = {"text": {"maxCharacters": 12000}}
        elif mode == "summary":
            contents = {"summary": True}
        elif mode == "highlights":
            contents = {"highlights": True}
        if freshness == "30d":
            contents["maxAgeHours"] = 24 * 30
        elif freshness == "90d":
            contents["maxAgeHours"] = 24 * 90
        elif freshness in {"live", "realtime"}:
            contents["maxAgeHours"] = 0
        return contents

    def _category_for_source_type(self, source_type: str) -> str | None:
        if source_type == "academic":
            return "research paper"
        if source_type == "news":
            return "news"
        if source_type == "company":
            return "company"
        return None

    def _normalize_exa_result(self, query: str, item: dict[str, Any], source_type: str) -> dict[str, Any]:
        highlights = item.get("highlights") or []
        highlight_scores = item.get("highlightScores") or []
        snippet = "\n".join(str(value) for value in highlights[:3]) or item.get("summary", "") or item.get("text", "")[:800]
        relevance_score = max(highlight_scores) if highlight_scores else 0.62
        url = item.get("url", "")
        return normalize_result(
            tool=self.name,
            query=query,
            title=item.get("title", ""),
            url=url,
            published_date=item.get("publishedDate") or "",
            source_type=source_type,
            publisher=item.get("author") or "",
            snippet=snippet,
            content=item.get("text", "") or item.get("summary", ""),
            relevance_score=relevance_score,
            credibility_score=credibility_for_url(url, source_type),
            freshness_score=0.65 if item.get("publishedDate") else 0.5,
            need_verification=True,
        )


class BraveTool(HttpSearchTool):
    name = "brave"
    async def search(self, query: str, max_results: int = 5, source_type: str = "webpage", freshness: str = "any") -> list[dict[str, Any]]:
        key = get_settings().brave_api_key
        if not key:
            return []
        data = await self._get_json("https://api.search.brave.com/res/v1/web/search", params={"q": query, "count": max_results}, headers={"X-Subscription-Token": key, "Accept": "application/json"})
        rows = data.get("web", {}).get("results", [])
        return [normalize_result(tool=self.name, query=query, title=i.get("title", ""), url=i.get("url", ""), snippet=i.get("description", ""), source_type=source_type, relevance_score=0.6, credibility_score=credibility_for_url(i.get("url", ""), source_type), freshness_score=0.6) for i in rows]


class SerpApiTool(HttpSearchTool):
    name = "serpapi"
    async def search(self, query: str, max_results: int = 5, source_type: str = "webpage", freshness: str = "any") -> list[dict[str, Any]]:
        key = get_settings().serpapi_api_key
        if not key:
            return []
        data = await self._get_json("https://serpapi.com/search.json", params={"q": query, "api_key": key, "num": max_results})
        rows = data.get("organic_results", []) or data.get("news_results", [])
        return [normalize_result(tool=self.name, query=query, title=i.get("title", ""), url=i.get("link", ""), snippet=i.get("snippet", ""), published_date=i.get("date", ""), source_type=source_type, relevance_score=0.58, credibility_score=credibility_for_url(i.get("link", ""), source_type), freshness_score=0.55) for i in rows[:max_results]]


class JinaReaderTool(HttpSearchTool):
    name = "jina_reader"
    async def read(self, url: str) -> str:
        if not url.startswith("http"):
            return ""
        return await self._get_text("https://r.jina.ai/http://" + url.removeprefix("https://").removeprefix("http://"))


class SearchPageFallbackTool:
    name = "search_page_fallback"
    async def search(self, query: str, max_results: int = 3, source_type: str = "webpage", freshness: str = "any") -> list[dict[str, Any]]:
        engines = [
            ("google", f"https://www.google.com/search?q={quote_plus(query)}"),
            ("bing", f"https://www.bing.com/search?q={quote_plus(query)}"),
        ]
        return [normalize_result(tool=name, query=query, title=f"{name.title()} 搜索入口：{query}", url=url, snippet="未配置对应 API，本条为人工核验入口。", source_type=source_type, relevance_score=0.3, credibility_score=0.2, freshness_score=0.2, need_verification=True) for name, url in engines[:max_results]]
