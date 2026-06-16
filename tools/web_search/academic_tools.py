from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from tools.web_search.base import HttpSearchTool, normalize_result


class OpenAlexTool(HttpSearchTool):
    name = "openalex"
    async def search(self, query: str, max_results: int = 5, source_type: str = "academic", freshness: str = "any") -> list[dict[str, Any]]:
        data = await self._get_json("https://api.openalex.org/works", params={"search": query, "per-page": max_results})
        rows = []
        for i in data.get("results", [])[:max_results]:
            rows.append(normalize_result(tool=self.name, query=query, title=i.get("title", ""), url=i.get("doi") or i.get("id", ""), published_date=str(i.get("publication_year", "")), source_type="academic", publisher=(i.get("primary_location") or {}).get("source", {}).get("display_name", "OpenAlex"), snippet="; ".join((i.get("abstract_inverted_index") or {}).keys())[:500], relevance_score=0.68, credibility_score=0.9, freshness_score=0.55, need_verification=False))
        return rows


class CrossrefTool(HttpSearchTool):
    name = "crossref"
    async def search(self, query: str, max_results: int = 5, source_type: str = "academic", freshness: str = "any") -> list[dict[str, Any]]:
        data = await self._get_json("https://api.crossref.org/works", params={"query": query, "rows": max_results})
        return [normalize_result(tool=self.name, query=query, title=(i.get("title") or [""])[0], url=i.get("URL", ""), published_date=str((i.get("published-print") or i.get("published-online") or {}).get("date-parts", [[""]])[0][0]), source_type="academic", publisher=(i.get("publisher") or "Crossref"), snippet=(i.get("abstract") or "")[:800], relevance_score=0.62, credibility_score=0.88, freshness_score=0.5, need_verification=False) for i in data.get("message", {}).get("items", [])[:max_results]]


class PubMedTool(HttpSearchTool):
    name = "pubmed"
    async def search(self, query: str, max_results: int = 5, source_type: str = "academic", freshness: str = "any") -> list[dict[str, Any]]:
        data = await self._get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={"db": "pubmed", "term": query, "retmode": "json", "retmax": max_results})
        ids = data.get("esearchresult", {}).get("idlist", [])
        return [normalize_result(tool=self.name, query=query, title=f"PubMed PMID {pmid}", url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/", source_type="academic", publisher="NCBI PubMed", snippet="生命科学/医学文献检索结果，需进入 PubMed 查看摘要和全文链接。", relevance_score=0.58, credibility_score=0.9, freshness_score=0.5, need_verification=False) for pmid in ids]


class SemanticScholarTool(HttpSearchTool):
    name = "semantic_scholar"
    async def search(self, query: str, max_results: int = 5, source_type: str = "academic", freshness: str = "any") -> list[dict[str, Any]]:
        data = await self._get_json("https://api.semanticscholar.org/graph/v1/paper/search", params={"query": query, "limit": max_results, "fields": "title,url,abstract,year,venue,citationCount"})
        return [normalize_result(tool=self.name, query=query, title=i.get("title", ""), url=i.get("url", ""), published_date=str(i.get("year", "")), source_type="academic", publisher=i.get("venue", "Semantic Scholar"), snippet=(i.get("abstract") or "")[:800], relevance_score=0.64, credibility_score=0.86, freshness_score=0.5, need_verification=False) for i in data.get("data", [])]


class ArxivTool(HttpSearchTool):
    name = "arxiv"
    async def search(self, query: str, max_results: int = 5, source_type: str = "academic", freshness: str = "any") -> list[dict[str, Any]]:
        text = await self._get_text("https://export.arxiv.org/api/query", params={"search_query": "all:" + query, "start": 0, "max_results": max_results})
        # 轻量解析，避免新增依赖。
        entries = text.split("<entry>")[1:]
        rows = []
        for entry in entries[:max_results]:
            title = entry.split("<title>", 1)[1].split("</title>", 1)[0].strip() if "<title>" in entry else "arXiv result"
            link = entry.split("href=\"", 1)[1].split("\"", 1)[0] if "href=\"" in entry else f"https://arxiv.org/search/?query={quote_plus(query)}&searchtype=all"
            summary = entry.split("<summary>", 1)[1].split("</summary>", 1)[0].strip() if "<summary>" in entry else ""
            rows.append(normalize_result(tool=self.name, query=query, title=title, url=link, snippet=summary, source_type="academic", publisher="arXiv", relevance_score=0.58, credibility_score=0.78, freshness_score=0.5, need_verification=False))
        return rows
