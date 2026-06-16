from __future__ import annotations

from typing import Any

from tools.web_search.duckduckgo_tool import DuckDuckGoTool


POLICY_DOMAINS = ["site:gov.cn", "site:miit.gov.cn", "site:most.gov.cn", "site:ndrc.gov.cn", "site:mee.gov.cn", "site:samr.gov.cn", "site:gov", "site:europa.eu", "site:energy.gov", "site:nih.gov", "site:nist.gov"]


class PolicySearchTool:
    name = "policy_search"
    def __init__(self) -> None:
        self.ddg = DuckDuckGoTool()

    async def search(self, query: str, max_results: int = 5, source_type: str = "policy", freshness: str = "12m") -> list[dict[str, Any]]:
        enriched = f"{query} 发布机构 发布时间 政策 原文 适用范围 ({' OR '.join(POLICY_DOMAINS[:6])})"
        rows = await self.ddg.search(enriched, max_results=max_results, source_type="policy", freshness=freshness)
        for row in rows:
            row["tool"] = self.name
            row["source_type"] = "policy"
            row["credibility_score"] = max(row.get("credibility_score", 0.0), 0.72)
            row["need_verification"] = True
        return rows
