from __future__ import annotations

from typing import Any

from app.services.document_service import DocumentService
from app.services.image_service import ImageService
from app.services.outline_service import OutlineService
from app.services.retrieval_service import RetrievalService
from app.services.storage import RunStorage


class SolutionAgent:
    def __init__(self) -> None:
        self.storage = RunStorage()
        self.documents = DocumentService()
        self.retrieval = RetrievalService()
        self.outlines = OutlineService()
        self.images = ImageService()

    async def create_run(self, title: str = "未命名解决方案") -> dict[str, Any]:
        return self.storage.create_run(title=title)

    async def generate_outline(self, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = payload.get("run_id")
        title = self._title(payload)
        if run_id:
            meta = self.storage.load_run(run_id)
            meta["title"] = title
        else:
            meta = self.storage.create_run(title=title)
            run_id = meta["run_id"]
        meta.update({
            "title": title,
            "domain": payload.get("domain", ""),
            "goal": payload.get("goal", ""),
            "scenario": payload.get("scenario", ""),
            "topic_count": payload.get("topic_count", 8),
            "user_input": payload,
        })
        self.storage.save_run(meta)
        self.storage.save_json(run_id, "input/user_input.json", payload)

        self.storage.update_status(run_id, "input", 8, "解析用户需求、目标受众和输出约束")
        self.storage.update_status(run_id, "documents", 20, "解析上传文档，提取标题、摘要、表格和样例")
        parsed_documents = await self.documents.parse_run_uploads(run_id, payload.get("uploaded_files"))

        self.storage.update_status(run_id, "retrieval_plan", 34, "生成政策、产业、学术、专利、新闻和竞品检索计划")
        self.storage.update_status(run_id, "retrieval", 52, "执行多源联网检索并按可信度/时效性排序")
        search_plan, retrieval_sources = await self.retrieval.retrieve(run_id, payload, parsed_documents)

        self.storage.update_status(run_id, "outline", 76, "GPT-5.5 正在综合证据并生成 Markdown 大纲")
        outline, topics, todos = await self.outlines.generate_outline(run_id, payload, parsed_documents, retrieval_sources)

        meta = self.storage.load_run(run_id)
        meta.update({"outline_markdown": outline, "topics": topics, "todos": todos, "retrieval_sources": retrieval_sources, "search_plan": search_plan})
        self.storage.save_run(meta)
        self.storage.update_status(run_id, "outline_done", 100, "解决方案大纲已生成，等待用户确认", status="done")
        return {"run_id": run_id, "title": title, "outline_markdown": outline, "todos": todos, "topics": topics, "retrieval_sources": retrieval_sources}

    async def generate_images(self, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = payload["run_id"]
        self.storage.update_status(run_id, "image_prompts", 18, "拆解用户确认后的 Markdown 并生成 topic prompts")
        self.storage.update_status(run_id, "image_generation", 52, "调用图片模型生成连续风格一致的解决方案图片")
        result = await self.images.generate_images(payload)
        errors = result.get("image_errors") or []
        if errors:
            self.storage.update_status(run_id, "images_done", 100, f"图片生成部分完成：成功 {len(result.get('images', []))} 张，失败 {len(errors)} 张", status="done")
        else:
            self.storage.update_status(run_id, "images_done", 100, "解决方案图片已生成", status="done")
        return result

    async def edit_image(self, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = payload["run_id"]
        self.storage.update_status(run_id, "image_edit", 45, "根据用户要求生成单图新版本")
        result = await self.images.edit_image(payload)
        self.storage.update_status(run_id, "image_edit_done", 100, "单图修改已保存", status="done")
        return result

    def status(self, run_id: str) -> dict[str, Any]:
        meta = self.storage.load_run(run_id)
        return {"run_id": run_id, **meta.get("status", {})}

    def _title(self, payload: dict[str, Any]) -> str:
        domain = payload.get("domain") or "解决方案"
        goal = payload.get("goal") or "方案生成"
        return f"{domain} · {goal}"
