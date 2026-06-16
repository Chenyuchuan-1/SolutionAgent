from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from app.models.openai_client import OpenAIClient
from app.prompts.outline_prompts import get_outline_generation_prompt
from app.prompts.system_prompts import detect_prompt_language, get_solution_system_prompt
from app.services.storage import RunStorage
from tools.citations.citation_formatter import markdown_link_source


class OutlineService:
    def __init__(self) -> None:
        self.openai = OpenAIClient()
        self.storage = RunStorage()

    async def generate_outline(self, run_id: str, payload: dict[str, Any], parsed_documents: list[dict[str, Any]], retrieval_sources: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
        output_language = detect_prompt_language(
            payload.get("domain", ""),
            payload.get("goal", ""),
            payload.get("scenario", ""),
            payload.get("prompt") or payload.get("user_prompt") or "",
        )
        parsed_document_summary = await self._summarize_documents(parsed_documents, payload)
        retrieval_summary = await self._summarize_sources(retrieval_sources, payload)
        parsed_document_context = self._documents_context_for_outline(parsed_document_summary)
        retrieval_context = self._retrieval_context_for_outline(retrieval_summary)
        self.storage.save_json(run_id, "parsed/parsed_documents_summary.json", parsed_document_summary)
        self.storage.save_json(run_id, "retrieval/search_results_summary.json", retrieval_summary)
        self.storage.save_text(run_id, "parsed/parsed_documents_outline_context.md", parsed_document_context)
        self.storage.save_text(run_id, "retrieval/search_results_outline_context.md", retrieval_context)
        prompt = get_outline_generation_prompt(output_language).format(
            domain=payload.get("domain", ""),
            goal=payload.get("goal", ""),
            scenario=payload.get("scenario", ""),
            user_prompt=payload.get("prompt") or payload.get("user_prompt") or "",
            parsed_documents=parsed_document_context,
            retrieval_results=retrieval_context,
            topic_count=payload.get("topic_count", 8),
        )
        self.storage.save_text(run_id, "prompts/outline_prompt.txt", prompt)
        self.storage.save_text(run_id, "prompts/system_prompt.txt", get_solution_system_prompt(output_language))
        outline = await self.openai.generate_outline(get_solution_system_prompt(output_language), prompt)
        if not outline:
            outline = self._fallback_outline(payload, parsed_documents, retrieval_sources)
        outline = outline.strip().strip("`")
        topics = self.extract_topics(outline, int(payload.get("topic_count", 8)))
        todos = [
            {"status": "done", "task": "解析用户需求与输出约束"},
            {"status": "done", "task": "解析上传文档并归档过程文件"},
            {"status": "done", "task": "规划并执行政策、产业、技术、学术、专利、新闻多源检索"},
            {"status": "done", "task": "构建 evidence map，标注需要核验的来源"},
            {"status": "todo", "task": "用户确认 Markdown 后生成连续风格一致的图片"},
        ]
        self.storage.save_text(run_id, "outline/outline.md", outline)
        self.storage.save_text(run_id, "outline/outline_versions/v01.md", outline)
        return outline, topics, todos

    async def _summarize_documents(self, parsed_documents: list[dict[str, Any]], payload: dict[str, Any]) -> list[dict[str, Any]]:
        semaphore = asyncio.Semaphore(2)
        async def summarize_one(doc: dict[str, Any]) -> dict[str, Any]:
            async with semaphore:
                try:
                    llm_summary = await self._deep_summarize_document(doc, payload)
                    if llm_summary:
                        return {**self._rule_summarize_document(doc), "llm_deep_summary": llm_summary, "summary_method": "deepseek_per_pdf"}
                except Exception:
                    pass
                return {**self._rule_summarize_document(doc), "summary_method": "rule_fallback"}

        return await asyncio.gather(*(summarize_one(doc) for doc in parsed_documents))

    def _documents_context_for_outline(self, document_summaries: list[dict[str, Any]]) -> str:
        """Build a balanced outline context so every uploaded document survives truncation."""
        if not document_summaries:
            return "无上传文档解析结果。"

        # DeepSeek summaries are already compressed; keep roughly one full summary per PDF.
        # The total document context therefore scales linearly with the number of documents.
        per_doc_summary_chars = 9000
        per_doc_fallback_chars = 1800
        blocks = []
        for index, doc in enumerate(document_summaries, start=1):
            title = doc.get("title") or doc.get("file") or f"Document {index}"
            llm_summary = self._strip_markdown_fence(str(doc.get("llm_deep_summary") or "")).strip()
            fallback_summary = self._compact_text(str(doc.get("summary") or ""))[:per_doc_fallback_chars]
            key_sections = []
            for section in (doc.get("key_sections") or [])[:4]:
                section_title = self._compact_text(str(section.get("section") or "section"))[:80]
                key_text = self._compact_text(str(section.get("key_text") or ""))[:320]
                if key_text:
                    key_sections.append(f"- {section_title}: {key_text}")

            blocks.append(
                "\n".join(
                    part
                    for part in [
                        f"## 文献 {index}: {title}",
                        f"- 文件：{doc.get('file', '')}",
                        f"- 解析状态：{doc.get('status', '')}",
                        f"- 类型：{doc.get('type', '')}",
                        f"- 压缩方式：{doc.get('summary_method', '')}",
                        "### DeepSeek 深度归纳",
                        (llm_summary[:per_doc_summary_chars] if llm_summary else fallback_summary),
                        "### 规则摘要 / 关键片段",
                        "\n".join(key_sections) if key_sections else fallback_summary,
                        "### 计数信息",
                        f"- 表格数量：{doc.get('table_count', 0)}；图片数量：{doc.get('figure_count', 0)}",
                    ]
                    if part
                )
            )

        return "\n\n---\n\n".join(blocks)

    async def _deep_summarize_document(self, doc: dict[str, Any], payload: dict[str, Any]) -> str | None:
        system_prompt = "你是面向企业解决方案咨询的科技文献分析专家。请把 PDF 解析内容深度归纳为后续解决方案大纲可用的结构化情报，不要复述全文。"
        user_prompt = f"""
用户领域：{payload.get("domain", "")}
用户目标：{payload.get("goal", "")}
应用场景：{payload.get("scenario", "")}

文档标题：{doc.get("title", "")}
文档摘要：
{self._compact_text(str(doc.get("summary") or ""))[:1800]}

关键正文片段：
{self._document_context(doc)}

请输出中文 Markdown，控制在 800-1200 字，结构固定为：
1. 文档核心结论
2. 与用户目标相关的可用依据
3. 可转化为解决方案的做法/模块/流程
4. 对图片脚本有价值的视觉元素
5. 需要人工核验的数字、实验结论或企业化假设

要求：
- 聚焦“如何为甲方形成解决方案”，不是论文综述。
- 保留关键方法、闭环流程、数据/模型/实验关系。
- 不要编造 DOI、政策、市场数据或企业事实。
""".strip()
        return await self.openai.summarize_with_deepseek(system_prompt, user_prompt)

    def _document_context(self, doc: dict[str, Any]) -> str:
        parts = []
        for chunk in (doc.get("chunks") or [])[:10]:
            section = str(chunk.get("section") or "chunk").strip()
            text = self._compact_text(str(chunk.get("text") or ""))[:900]
            if text:
                parts.append(f"## {section}\n{text}")
        tables = [self._compact_text(str(item.get("caption") or item.get("text") or ""))[:180] for item in (doc.get("tables") or [])[:5]]
        figures = [self._compact_text(str(item.get("caption") or ""))[:180] for item in (doc.get("figures") or [])[:5]]
        if tables:
            parts.append("## 表格摘要\n" + "\n".join(f"- {item}" for item in tables if item))
        if figures:
            parts.append("## 图片摘要\n" + "\n".join(f"- {item}" for item in figures if item))
        return "\n\n".join(parts)[:12000]

    def _rule_summarize_document(self, doc: dict[str, Any]) -> dict[str, Any]:
        chunks = doc.get("chunks") or []
        chunk_summaries = []
        seen_sections: set[str] = set()
        for chunk in chunks:
            section = str(chunk.get("section") or "chunk").strip()
            text = self._compact_text(str(chunk.get("text") or ""))
            if not text or section in seen_sections:
                continue
            seen_sections.add(section)
            chunk_summaries.append({"section": section[:80], "key_text": text[:420]})
            if len(chunk_summaries) >= 5:
                break
        tables = doc.get("tables") or []
        figures = doc.get("figures") or []
        return {
            "file": doc.get("file"),
            "status": doc.get("status"),
            "type": doc.get("type"),
            "title": doc.get("title"),
            "summary": self._compact_text(str(doc.get("summary") or ""))[:900],
            "key_sections": chunk_summaries,
            "table_count": len(tables),
            "table_captions": [self._compact_text(str(item.get("caption") or item.get("text") or ""))[:160] for item in tables[:3]],
            "figure_count": len(figures),
            "figure_captions": [self._compact_text(str(item.get("caption") or ""))[:160] for item in figures[:3]],
            "mineru": doc.get("mineru", {}),
        }

    def _rule_summarize_documents(self, parsed_documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        summarized = []
        for doc in parsed_documents:
            summarized.append(self._rule_summarize_document(doc))
        return summarized

    async def _summarize_sources(self, retrieval_sources: list[dict[str, Any]], payload: dict[str, Any]) -> list[dict[str, Any]]:
        batches = [retrieval_sources[index:index + 5] for index in range(0, len(retrieval_sources), 5)]
        summarized = []
        for index, batch in enumerate(batches, start=1):
            try:
                llm_summary = await self._deep_summarize_source_batch(batch, payload, index)
                if llm_summary:
                    summarized.append({"batch": index, "summary_method": "deepseek_per_5_sources", "llm_deep_summary": llm_summary, "sources": self._rule_summarize_sources(batch)})
                    continue
            except Exception:
                pass
            summarized.append({"batch": index, "summary_method": "rule_fallback", "sources": self._rule_summarize_sources(batch)})
        return summarized

    async def _deep_summarize_source_batch(self, sources: list[dict[str, Any]], payload: dict[str, Any], batch_index: int) -> str | None:
        system_prompt = "你是企业咨询项目中的开源情报分析专家。请将搜索结果归纳成可用于解决方案大纲的证据与方案洞察。"
        source_payload = self._rule_summarize_sources(sources)
        user_prompt = f"""
用户领域：{payload.get("domain", "")}
用户目标：{payload.get("goal", "")}
应用场景：{payload.get("scenario", "")}

这是第 {batch_index} 组开源信息，每组最多 5 条：
{json.dumps(source_payload, ensure_ascii=False)}

请输出中文 Markdown，控制在 500-800 字，结构固定为：
1. 这组信息支持的关键判断
2. 对甲方解决方案设计的启发
3. 可落成的模块、流程或试点场景
4. 需要核验或不适合直接对外引用的点

要求：
- 不要逐条复述搜索结果。
- 不要编造数据、政策编号、企业事实。
- 把政策/产业/技术/学术信息分开归纳。
""".strip()
        return await self.openai.summarize_with_deepseek(system_prompt, user_prompt)

    def _rule_summarize_sources(self, retrieval_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        summarized = []
        for source in retrieval_sources:
            summarized.append({
                "source_id": source.get("source_id"),
                "title": source.get("title"),
                "url": source.get("url"),
                "published_date": source.get("published_date"),
                "source_type": source.get("source_type"),
                "publisher": source.get("publisher"),
                "snippet": self._compact_text(str(source.get("snippet") or source.get("content") or ""))[:420],
                "tool": source.get("tool"),
                "confidence": source.get("confidence"),
                "need_verification": source.get("need_verification"),
                "final_score": source.get("final_score"),
            })
        return summarized

    def _retrieval_context_for_outline(self, retrieval_summary: list[dict[str, Any]]) -> str:
        if not retrieval_summary:
            return "无联网检索结果。"
        per_batch_summary_chars = 10000
        per_source_chars = 700
        blocks = []
        for item in retrieval_summary:
            batch_index = item.get("batch", len(blocks) + 1)
            summary = self._strip_markdown_fence(str(item.get("llm_deep_summary") or "")).strip()
            sources = item.get("sources") or []
            source_lines = []
            for source in sources:
                source_lines.append(
                    "\n".join(
                        part
                        for part in [
                            f"- 标题：{source.get('title', '')}",
                            f"  URL：{source.get('url', '')}",
                            f"  来源类型：{source.get('source_type', '')}；发布日期：{source.get('published_date', '')}；可信度：{source.get('confidence', '')}；需核验：{source.get('need_verification', '')}",
                            f"  摘要：{self._compact_text(str(source.get('snippet') or ''))[:per_source_chars]}",
                        ]
                        if part
                    )
                )
            blocks.append(
                "\n".join(
                    part
                    for part in [
                        f"## 检索批次 {batch_index}",
                        f"- 压缩方式：{item.get('summary_method', '')}",
                        "### DeepSeek 批次归纳",
                        summary[:per_batch_summary_chars] if summary else "本批次未生成 DeepSeek 归纳，使用规则摘要。",
                        "### 本批次来源",
                        "\n".join(source_lines),
                    ]
                    if part
                )
            )
        return "\n\n---\n\n".join(blocks)

    def _compact_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text.replace("\u0000", " ")).strip()
        text = re.sub(r"([。！？.!?])\s+", r"\1 ", text)
        return text

    def _strip_markdown_fence(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"^```(?:markdown|md)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        return text.strip()

    def extract_topics(self, outline: str, topic_count: int) -> list[dict[str, Any]]:
        headings = re.findall(r"^###\s+(T?\d{1,2})[\.\s-]*(.+)$", outline, flags=re.MULTILINE)
        topics = []
        for idx, (_, title) in enumerate(headings[:topic_count], start=1):
            topics.append({"topic_id": f"T{idx:02d}", "title": title.strip(), "goal": "见详细解决方案", "content": self._section_for(outline, title)})
        if len(topics) < topic_count:
            defaults = ["需求理解与目标定义", "政策与标准环境扫描", "产业链与竞品格局", "技术路线设计", "数据与文档解析方案", "Agent 工具编排", "可视化图片脚本", "实施计划与里程碑", "风险控制与合规", "评估指标与复盘机制", "商业化与交付方式", "未来扩展路线", "团队分工", "预算与资源", "验收清单"]
            for i in range(len(topics)+1, topic_count+1):
                topics.append({"topic_id": f"T{i:02d}", "title": defaults[i-1], "goal": "补充方案 topic", "content": defaults[i-1]})
        return topics

    def _section_for(self, outline: str, title: str) -> str:
        marker = title.strip()
        pos = outline.find(marker)
        if pos < 0:
            return marker
        next_pos = outline.find("\n### ", pos + len(marker))
        return outline[pos: next_pos if next_pos > pos else pos + 1600]

    def _fallback_outline(self, payload: dict[str, Any], parsed_documents: list[dict[str, Any]], sources: list[dict[str, Any]]) -> str:
        domain = payload.get("domain") or "解决方案"
        goal = payload.get("goal") or "形成可落地方案"
        scenario = payload.get("scenario") or "项目汇报与实施规划"
        prompt = payload.get("prompt") or payload.get("user_prompt") or ""
        count = int(payload.get("topic_count", 8))
        title = f"{domain}解决方案生成 Agent 方案"
        source_rows = "\n".join(
            f"| {markdown_link_source(s)} | {s.get('source_type')} | {s.get('published_date') or '需要核验'} | {s.get('snippet','')[:80]} | {s.get('confidence')} | {s.get('url')} |"
            for s in sources[:10]
        ) or "| 未找到可靠来源，建议人工核验 | - | - | 需要人工补充权威来源 | low | - |"
        topic_names = ["需求理解与边界", "政策与标准依据", "产业趋势与市场机会", "技术路线与系统架构", "数据与文档解析", "Agent 工具编排", "交付物与可视化", "实施路线图", "风险合规矩阵", "验收指标", "竞品与商业模式", "运维与成本", "组织分工", "扩展路线", "复盘机制"][:count]
        topic_rows = "\n".join(f"| T{i:02d} | {name} | 支撑 {goal} | 用信息图、架构图、流程图、矩阵或路线图呈现关键内容 | 需要核验 |" for i, name in enumerate(topic_names, 1))
        details = "\n\n".join(f"### T{i:02d} {name}\n\n* 核心问题：围绕 {domain} 在 {scenario} 中的关键决策点展开。\n* 解决思路：结合上传文档、政策/产业检索和技术路线形成 todo 型任务。\n* 需要的数据/工具/模型：GPT-5.5、文档解析、Tavily/DuckDuckGo/SearXNG、政策/产业/学术检索工具。\n* 产业或政策依据：优先使用已检索 URL；缺失处标记需要核验。\n* 可视化表达建议：使用内容丰富的信息图表达，包含中心主流程、左侧依据、右侧交付价值、关键指标和风险提示。" for i, name in enumerate(topic_names, 1))
        return f"""# {title}

## 1. 用户需求摘要

用户希望围绕“{domain}”在“{scenario}”中实现“{goal}”。原始提示词：{prompt or '未提供额外提示词'}。

本大纲基于上传文档 {len(parsed_documents)} 份和多源检索结果生成。未能从可靠来源确认的信息均标注为“需要核验”。

## 2. 目标与边界

| 类型 | 内容 |
|---|---|
| 目标 | {goal} |
| 非目标 | 不替代人工政策合规审查，不编造政策、市场规模或论文结论 |
| 受众 | 政府项目、企业汇报、科研平台或产品团队 |
| 交付物 | 可编辑 Markdown 大纲、topic 图片脚本、连续解决方案图片、历史归档 |
| 约束 | 来源可追溯，用户确认后的大纲作为图片最终依据 |

## 3. Todo 型任务拆解

- [x] 解析用户领域、目标、场景和输出约束
- [x] 解析上传文档并保存 parsed_documents.json
- [x] 规划政策、产业、学术、专利、标准、新闻和竞品检索 query
- [x] 汇总证据并标记需要核验项
- [ ] 用户确认 Markdown 大纲
- [ ] 生成统一风格的 image prompt 和方案图片
- [ ] 支持单图对话式修改与版本管理

## 4. 政策、产业与技术依据

| 来源标题 | 来源类型 | 日期 | 关键结论 | 可信度 | 链接 |
|---|---|---|---|---|---|
{source_rows}

## 5. 总体解决方案架构

方案采用“输入解析 -> 文档解析 -> 多源检索 -> 证据排序 -> GPT-5.5 大纲生成 -> 用户确认 -> 图片 prompt 生成 -> gpt-image-2 生成/编辑 -> JSON 归档”的流程。系统将业务需求、文档证据、外部来源和图片交付统一到 run 级目录中，便于复现和审计。

## 6. Topic 列表

| 编号 | Topic | 目标 | 需要呈现的图像内容 | 关键依据 |
|---|---|---|---|---|
{topic_rows}

## 7. 详细解决方案

{details}

## 8. 实施路线图

| 阶段 | 重点任务 | 交付物 |
|---|---|---|
| MVP | 打通上传、检索、大纲和 mock 图片 | 可运行 Demo |
| 内测 | 接入 OpenAI/Tavily/MinerU，完善错误处理 | 真实大纲和图片 |
| 试点 | 选择 1-2 个领域模板验证 | 可复用案例 |
| 上线 | 加入权限、配额、监控和 SQLite | 产品化版本 |
| 迭代 | 多模型、多检索源和协作审阅 | 行业解决方案平台 |

## 9. 风险矩阵

| 风险类型 | 风险描述 | 影响 | 概率 | 控制措施 |
|---|---|---|---|---|
| 信息真实性 | 检索入口或摘要不足以支撑结论 | 高 | 中 | 保留 URL、日期和需要核验标记 |
| 政策合规 | 政策适用范围误读 | 高 | 中 | 优先政府/标准机构来源并人工复核 |
| 图片误导 | 图片出现未经核验数据或真实 Logo | 中 | 中 | prompt 禁止伪造编号、Logo、具体未核验数据 |
| 成本 | 多图生成调用成本较高 | 中 | 中 | topic 数量限制 5-15，失败可重试 |

## 10. 验收指标

| 指标 | 定义 | 目标值 | 评估方式 |
|---|---|---|---|
| 可运行性 | FastAPI 首页和 API 可启动 | 100% | uvicorn 启动检查 |
| 归档完整性 | run 下 meta、outline、prompts、images 可追溯 | 100% | 文件检查 |
| 来源可追溯 | 重要结论有 URL 或需要核验标记 | >=90% | 人工抽检 |
| 图片一致性 | 同 run 图片风格和编号一致 | >=90% | 视觉检查 |

## 11. 图片生成计划

每个 topic 生成一张横版 16:9 企业级解决方案信息图，重点呈现流程、架构、证据、指标、风险和交付物。图片 prompt 禁止使用未经核验的具体政策编号、市场规模和真实公司 Logo。
"""
