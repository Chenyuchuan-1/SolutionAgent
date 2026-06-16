from __future__ import annotations

import asyncio
from typing import Any

from app.core.logging import get_logger
from app.services.storage import RunStorage
from tools.citations.source_ranker import rank_sources
from tools.web_search.academic_tools import ArxivTool, CrossrefTool, OpenAlexTool, PubMedTool, SemanticScholarTool
from tools.web_search.duckduckgo_tool import DuckDuckGoTool
from tools.web_search.industry_search_tool import IndustrySearchTool
from tools.web_search.policy_search_tool import PolicySearchTool
from tools.web_search.tavily_tool import TavilyTool
from tools.web_search.universal_tools import BraveTool, ExaTool, SearchPageFallbackTool, SerpApiTool

logger = get_logger(__name__)


class RetrievalService:
    def __init__(self) -> None:
        self.storage = RunStorage()
        self.tools = {
            "tavily": TavilyTool(),
            "exa": ExaTool(),
            "brave": BraveTool(),
            "serpapi": SerpApiTool(),
            "duckduckgo": DuckDuckGoTool(),
            "policy_search": PolicySearchTool(),
            "industry_search": IndustrySearchTool(),
            "openalex": OpenAlexTool(),
            "crossref": CrossrefTool(),
            "pubmed": PubMedTool(),
            "semantic_scholar": SemanticScholarTool(),
            "arxiv": ArxivTool(),
            "fallback": SearchPageFallbackTool(),
        }

    def plan_queries(self, payload: dict[str, Any], parsed_documents: list[dict[str, Any]]) -> dict[str, Any]:
        domain = payload.get("domain") or "用户领域"
        goal = payload.get("goal") or payload.get("prompt") or "解决方案生成"
        scenario = payload.get("scenario") or "应用场景"
        base = f"{domain} {goal} {scenario}".strip()
        queries = [
            {"query": f"{base} 政策 法规 标准 近两年", "category": "policy", "freshness": "12m", "priority": "high", "preferred_tools": ["policy_search", "tavily", "serpapi"], "domains": ["gov", "gov.cn", "europa.eu", "org"], "reason": "政策、法规、标准依据必须检索并保留原文来源"},
            {"query": f"{base} 产业趋势 市场规模 头部企业 白皮书", "category": "industry", "freshness": "12m", "priority": "high", "preferred_tools": ["industry_search", "tavily", "brave", "exa"], "domains": ["org", "company"], "reason": "产业和市场判断需要近期外部来源支撑"},
            {"query": f"{base} 技术路线 架构 工具链 最佳实践", "category": "technology", "freshness": "12m", "priority": "medium", "preferred_tools": ["tavily", "exa", "duckduckgo"], "domains": ["edu", "org", "github"], "reason": "形成技术路线与工具编排依据"},
            {"query": f"{base} academic paper review survey", "category": "academic", "freshness": "any", "priority": "medium", "preferred_tools": ["openalex", "crossref", "semantic_scholar", "arxiv", "pubmed"], "domains": ["edu", "org"], "reason": "检索论文、综述和学术证据，且与产业结论分开标注"},
            {"query": f"{base} patent 技术 专利 申请人 法律状态", "category": "patent", "freshness": "any", "priority": "low", "preferred_tools": ["serpapi", "duckduckgo", "fallback"], "domains": ["patents.google.com", "wipo.int", "espacenet.com"], "reason": "识别企业技术路线和专利证据"},
            {"query": f"{base} 新闻 最新动态 30天 90天", "category": "news", "freshness": "90d", "priority": "medium", "preferred_tools": ["brave", "serpapi", "duckduckgo"], "domains": ["news"], "reason": "区分近 30 天、90 天和 12 个月的时效性信息"},
            {"query": f"{base} 竞品 产品 功能边界 商业化 客户案例", "category": "company", "freshness": "12m", "priority": "medium", "preferred_tools": ["exa", "brave", "duckduckgo"], "domains": ["company", "github"], "reason": "识别已有产品、商业化路径和差异化机会"},
        ]
        if parsed_documents:
            queries.append({"query": f"{domain} 上传文档观点 外部核验", "category": "standard", "freshness": "any", "priority": "medium", "preferred_tools": ["tavily", "duckduckgo", "openalex"], "domains": ["gov", "edu", "org"], "reason": "对上传文档中的关键结论进行外部交叉核验"})
        return {"queries": queries}

    async def retrieve(self, run_id: str, payload: dict[str, Any], parsed_documents: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        plan = self.plan_queries(payload, parsed_documents)
        self.storage.save_json(run_id, "retrieval/search_plan.json", plan)
        tasks = [self._run_query(item) for item in plan["queries"]]
        batches = await asyncio.gather(*tasks, return_exceptions=True)
        results: list[dict[str, Any]] = []
        for batch in batches:
            if isinstance(batch, Exception):
                logger.warning("retrieval failed: %s", batch)
                continue
            results.extend(batch)
        deduped = self._dedupe(results)
        ranked = rank_sources(deduped)[:60]
        self.storage.save_json(run_id, "retrieval/search_results.json", ranked)
        return plan, ranked

    async def _run_query(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for tool_name in item.get("preferred_tools", [])[:4]:
            tool = self.tools.get(tool_name)
            if not tool:
                continue
            try:
                rows.extend(await tool.search(item["query"], max_results=4, source_type=item["category"], freshness=item.get("freshness", "any")))
            except Exception as exc:
                logger.info("tool %s failed: %s", tool_name, exc)
        if not rows:
            rows.extend(await self.tools["fallback"].search(item["query"], max_results=2, source_type=item["category"], freshness=item.get("freshness", "any")))
        return rows

    def _dedupe(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        output = []
        for row in rows:
            key = (row.get("url") or row.get("title") or row.get("source_id") or "").lower()
            if not key or key in seen:
                continue
            seen.add(key)
            output.append(row)
        return output
