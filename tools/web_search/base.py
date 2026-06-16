from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

import httpx


def source_id(tool: str, url: str, title: str = "") -> str:
    raw = f"{tool}:{url}:{title}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:16]


def normalize_result(
    *, tool: str, query: str, title: str, url: str, source_type: str = "webpage", publisher: str = "", snippet: str = "", content: str = "", published_date: str | None = None,
    relevance_score: float = 0.55, credibility_score: float = 0.4, freshness_score: float = 0.4, need_verification: bool = True,
) -> dict[str, Any]:
    confidence = "high" if min(relevance_score, credibility_score) >= 0.75 else "medium" if relevance_score >= 0.45 else "low"
    return {
        "source_id": source_id(tool, url, title),
        "title": title or "Untitled source",
        "url": url,
        "published_date": published_date or "",
        "source_type": source_type,
        "publisher": publisher,
        "snippet": snippet,
        "content": content,
        "tool": tool,
        "query": query,
        "relevance_score": round(float(relevance_score), 3),
        "credibility_score": round(float(credibility_score), 3),
        "freshness_score": round(float(freshness_score), 3),
        "confidence": confidence,
        "need_verification": need_verification,
    }


def credibility_for_url(url: str, source_type: str) -> float:
    lowered = (url or "").lower()
    if source_type in {"policy", "standard", "academic"} or any(domain in lowered for domain in [".gov", "gov.cn", "europa.eu", "nih.gov", "nist.gov", "iso.org", "openalex.org", "crossref.org", "pubmed"]):
        return 0.9
    if source_type == "patent" or any(domain in lowered for domain in ["patents.google", "wipo", "espacenet", "lens.org"]):
        return 0.82
    if any(domain in lowered for domain in [".edu", ".org", "association", "standard"]):
        return 0.72
    if source_type in {"industry", "company"}:
        return 0.62
    if source_type == "news":
        return 0.56
    return 0.42


class HttpSearchTool:
    name = "http_search"
    timeout = 20.0

    async def _get_json(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()

    async def _get_text(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> str:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.text

    async def _post_json(self, url: str, json_data: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(url, json=json_data or {}, headers=headers)
            response.raise_for_status()
            return response.json()
