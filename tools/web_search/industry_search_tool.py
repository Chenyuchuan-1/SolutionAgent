from __future__ import annotations

from typing import Any

from tools.web_search.duckduckgo_tool import DuckDuckGoTool
from tools.web_search.universal_tools import BraveTool, ExaTool, SerpApiTool


class IndustrySearchTool:
    name = "industry_search"
    def __init__(self) -> None:
        self.tools = [ExaTool(), BraveTool(), SerpApiTool(), DuckDuckGoTool()]

    async def search(self, query: str, max_results: int = 5, source_type: str = "industry", freshness: str = "12m") -> list[dict[str, Any]]:
        expanded = f"{query} 市场规模 增长率 头部企业 产业报告 白皮书 供应链 商业模式"
        rows: list[dict[str, Any]] = []
        for tool in self.tools:
            try:
                rows.extend(await tool.search(expanded, max_results=max(1, max_results // 2), source_type=source_type, freshness=freshness))
            except Exception:
                continue
            if len(rows) >= max_results:
                break
        return rows[:max_results]
