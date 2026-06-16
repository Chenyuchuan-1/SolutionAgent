from __future__ import annotations

import asyncio
import base64
import html
import re
from typing import Any

from app.core.config import get_settings
from app.models.openai_client import OpenAIClient
from app.models.openai_client import OpenAIClientError
from app.prompts.edit_prompts import get_image_edit_prompt
from app.prompts.image_prompts import get_image_style_lock_prompt, get_single_topic_image_prompt_template
from app.prompts.system_prompts import detect_prompt_language
from app.services.storage import RunStorage, now_iso


class ImageService:
    def __init__(self) -> None:
        self.storage = RunStorage()
        self.openai = OpenAIClient()
        self.settings = get_settings()

    async def generate_images(self, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = payload["run_id"]
        meta = self.storage.load_run(run_id)
        outline = payload.get("outline_markdown") or meta.get("outline_markdown", "")
        topic_count = int(payload.get("topic_count") or meta.get("topic_count") or 8)
        topics = self._topics_from_outline(outline, meta.get("topics", []), topic_count)
        size = self._image_size(payload.get("image_size"), payload.get("aspect_ratio", "16:9"))
        quality = self.settings.default_image_quality
        prompts = []
        images = []
        title = self._title_from_outline(outline) or meta.get("title", "解决方案")
        output_language = detect_prompt_language(title, outline)
        base_style_lock_prompt = get_image_style_lock_prompt(output_language)
        drawing_style_lock = self._drawing_style_lock(outline)
        style_lock_prompt = self._merge_style_lock(base_style_lock_prompt, drawing_style_lock)
        image_prompt_template = get_single_topic_image_prompt_template(output_language)
        if not self.settings.openai_api_key and not self.settings.openai_image_url and not self.settings.mock_image_fallback:
            raise OpenAIClientError("OPENAI_API_KEY / OPENAI_IMAGE_URL 均缺失，已阻止 SVG mock fallback。请配置图片模型后重新生成图片。")
        concurrency = max(1, min(int(self.settings.image_generation_concurrency), len(topics)))
        semaphore = asyncio.Semaphore(concurrency)
        self.storage.save_json(run_id, "images/parsed_drawing_topics.json", topics)

        tasks = [
            self._generate_topic_image(
                semaphore=semaphore,
                run_id=run_id,
                topic=topic,
                idx=idx,
                total=len(topics),
                title=title,
                prompt_template=image_prompt_template,
                style_lock_prompt=style_lock_prompt,
                aspect_ratio=payload.get("aspect_ratio", "16:9"),
                size=size,
                quality=quality,
            )
            for idx, topic in enumerate(topics, start=1)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        image_errors = []
        for idx, result in enumerate(results, start=1):
            topic = topics[idx - 1]
            if isinstance(result, Exception):
                image_errors.append({
                    "image_index": topic.get("image_index", f"P{idx:02d}"),
                    "topic_id": topic.get("topic_id", f"T{idx:02d}"),
                    "topic_title": topic.get("title", ""),
                    "error": str(result) or result.__class__.__name__,
                    "error_type": result.__class__.__name__,
                    "created_at": now_iso(),
                })
                continue
            prompt_record, image = result
            prompts.append(prompt_record)
            images.append(image)
        self.storage.save_json(run_id, "prompts/topic_prompts.json", prompts)
        self.storage.save_json(run_id, "images/image_errors.json", image_errors)
        meta["outline_markdown"] = outline
        meta["topics"] = topics
        meta["images"] = images
        meta["image_errors"] = image_errors
        self.storage.save_run(meta)
        return {"run_id": run_id, "images": images, "prompts": prompts, "image_errors": image_errors}

    async def _generate_topic_image(
        self,
        *,
        semaphore: asyncio.Semaphore,
        run_id: str,
        topic: dict[str, Any],
        idx: int,
        total: int,
        title: str,
        prompt_template: str,
        style_lock_prompt: str,
        aspect_ratio: str,
        size: str,
        quality: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        prompt = prompt_template.format(
            index=idx,
            total=total,
            image_index=topic.get("image_index", f"P{idx:02d}"),
            solution_title=title,
            topic_title=topic["title"],
            topic_content=topic.get("content", topic["title"]),
            style_lock_prompt=style_lock_prompt,
            aspect_ratio=aspect_ratio,
        )
        async with semaphore:
            image_bytes = await self.openai.generate_image(prompt, size=size, quality=quality)
        ext = "png"
        if not image_bytes:
            if not self.settings.mock_image_fallback:
                raise OpenAIClientError("图片模型未返回图像数据，已阻止 SVG mock fallback。请检查 OPENAI_IMAGE_URL、OPENAI_IMAGE_MODEL 和 API 返回格式。")
            image_bytes = self._mock_svg(idx, total, topic["title"], title).encode("utf-8")
            ext = "svg"
        filename = f"{topic['topic_id']}_v01.{ext}"
        self.storage.save_bytes(run_id, f"images/{filename}", image_bytes)
        created_at = now_iso()
        prompt_record = {
            "topic_id": topic["topic_id"],
            "topic_title": topic["title"],
            "image_prompt": prompt,
            "style_lock_prompt": style_lock_prompt,
            "model": self.settings.openai_image_model,
            "size": size,
            "quality": quality,
            "output_path": str(self.storage.run_dir(run_id) / "images" / filename),
            "generation_mode": "mock_svg" if ext == "svg" else "model",
            "created_at": created_at,
        }
        image = {
            "image_id": topic["topic_id"],
            "topic_id": topic["topic_id"],
            "title": topic["title"],
            "url": self.storage.public_image_url(run_id, filename),
            "filename": filename,
            "prompt": prompt,
            "style_lock_prompt": style_lock_prompt,
            "model": self.settings.openai_image_model,
            "size": size,
            "quality": quality,
            "generation_mode": "mock_svg" if ext == "svg" else "model",
            "version": 1,
            "versions": [{"version": 1, "filename": filename, "url": self.storage.public_image_url(run_id, filename), "created_at": created_at}],
            "edits": [],
            "created_at": created_at,
        }
        return prompt_record, image

    async def edit_image(self, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = payload["run_id"]
        instruction = payload["instruction"]
        meta = self.storage.load_run(run_id)
        images = meta.get("images", [])
        image = next((item for item in images if item.get("image_id") == payload["image_id"]), None)
        if not image:
            raise ValueError("Image not found")
        source_filename = image.get("filename")
        source_path = self.storage.run_dir(run_id) / "images" / source_filename if source_filename else None
        if not source_path or not source_path.exists():
            raise OpenAIClientError("找不到当前图片原始文件，无法执行基于原图的 image edit。")
        if source_path.suffix.lower() == ".svg" and not self.settings.mock_image_fallback:
            raise OpenAIClientError("当前图片是 SVG mock，不支持真实 image edit。请先使用真实图片模型生成 PNG/JPG 后再修改。")
        total = len(images)
        index = images.index(image) + 1
        output_language = detect_prompt_language(meta.get("title", ""), image.get("title", ""), image.get("prompt", ""), instruction)
        edit_prompt = get_image_edit_prompt(output_language).format(
            solution_title=meta.get("title", "解决方案"),
            image_index=index,
            total=total,
            topic_title=image.get("title", ""),
            original_prompt=image.get("prompt", ""),
            edit_instruction=instruction,
        )
        version = int(image.get("version", 1)) + 1
        if not self.settings.openai_api_key and not self.settings.openai_image_url and not self.settings.openai_image_edit_url and not self.settings.mock_image_fallback:
            raise OpenAIClientError("OPENAI_API_KEY / OPENAI_IMAGE_URL 均缺失，无法调用图片编辑模型。")
        image_bytes = await self.openai.edit_image(edit_prompt, source_path, size=image.get("size") or self.settings.default_image_size, quality=image.get("quality") or self.settings.default_image_quality)
        ext = "png"
        if not image_bytes:
            if not self.settings.mock_image_fallback:
                raise OpenAIClientError("图片编辑模型未返回图像数据，已阻止 SVG mock fallback。")
            image_bytes = self._mock_svg(index, total, image.get("title", ""), meta.get("title", "解决方案"), instruction=instruction, version=version).encode("utf-8")
            ext = "svg"
        filename = f"{image['topic_id']}_v{version:02d}.{ext}"
        self.storage.save_bytes(run_id, f"images/{filename}", image_bytes)
        record = {"role": "user", "content": instruction, "created_at": now_iso()}
        reply = {"role": "agent", "content": f"已生成第 {version} 版图片，并保留原图风格与编号。", "created_at": now_iso(), "version": version}
        image.setdefault("edits", []).extend([record, reply])
        image.setdefault("versions", []).append({"version": version, "filename": filename, "url": self.storage.public_image_url(run_id, filename), "created_at": now_iso(), "instruction": instruction, "source_filename": source_filename})
        image.update({"version": version, "filename": filename, "url": self.storage.public_image_url(run_id, filename)})
        edit_history = {"image_id": image["image_id"], "version": version, "instruction": instruction, "prompt": edit_prompt, "filename": filename, "source_filename": source_filename, "generation_mode": "mock_svg" if ext == "svg" else "model_edit", "created_at": now_iso()}
        meta.setdefault("edit_history", []).append(edit_history)
        self.storage.save_json(run_id, f"edits/{image['topic_id']}_edits.json", image.get("edits", []))
        self.storage.save_run(meta)
        return {"run_id": run_id, "images": images, "edit_history": meta.get("edit_history", [])}

    def _topics_from_outline(self, outline: str, existing: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
        drawing_topics = self._topics_from_drawing_plan(outline, count)
        if drawing_topics:
            return drawing_topics
        headings = re.findall(r"^###\s+(T?\d{1,2})[\.\s-]*(.+)$", outline, flags=re.MULTILINE)
        topics = []
        for idx, (_, title) in enumerate(headings[:count], 1):
            topic_id = f"T{idx:02d}"
            section = self._section(outline, title)
            page_script = self._page_script_for(outline, idx, topic_id)
            content = self._drawing_content(page_script, section)
            topics.append({"topic_id": topic_id, "image_index": f"P{idx:02d}", "title": title.strip(), "content": content})
        if len(topics) < count:
            for idx, item in enumerate(existing[len(topics):count], len(topics) + 1):
                topic_id = item.get("topic_id", f"T{idx:02d}")
                page_script = self._page_script_for(outline, idx, topic_id)
                content = self._drawing_content(page_script, item.get("content", item.get("title", "")))
                topics.append({"topic_id": topic_id, "image_index": f"P{idx:02d}", "title": item.get("title", f"Topic {idx}"), "content": content})
        while len(topics) < count:
            idx = len(topics) + 1
            topic_id = f"T{idx:02d}"
            page_script = self._page_script_for(outline, idx, topic_id)
            topics.append({"topic_id": topic_id, "image_index": f"P{idx:02d}", "title": f"Topic {idx}", "content": self._drawing_content(page_script, "从用户确认的大纲中补充生成")})
        return topics

    def _topics_from_drawing_plan(self, outline: str, count: int) -> list[dict[str, Any]]:
        section = self._drawing_plan_section(outline)
        if not section:
            return []
        rows = []
        for line in section.splitlines():
            cells = self._drawing_row_cells(line)
            if len(cells) < 7:
                continue
            if not re.fullmatch(r"P\d{2}", cells[0].strip()):
                continue
            if re.fullmatch(r":?-{3,}:?", cells[1].replace(" ", "")):
                continue
            rows.append(cells)
        topics = []
        for idx, cells in enumerate(rows[:count], start=1):
            image_index = cells[0].strip()
            topic_id = cells[1].strip() if re.fullmatch(r"T\d{2}", cells[1].strip()) else f"T{idx:02d}"
            title = cells[2].strip() or f"Topic {idx}"
            content = self._drawing_row_content(cells)
            topics.append({
                "topic_id": topic_id,
                "image_index": image_index,
                "title": title,
                "content": content,
                "source": "drawing_plan",
            })
        return topics

    def _drawing_plan_section(self, outline: str) -> str:
        match = re.search(r"^##\s+11\.\s+.*?(详细解决方案绘图提示词|Detailed Solution Drawing Prompts).*$", outline, flags=re.MULTILINE)
        if not match:
            match = re.search(r"^##\s+.*?(图片生成计划|Image Generation Plan).*$", outline, flags=re.MULTILINE)
        if not match:
            return ""
        next_match = re.search(r"^##\s+\d+\.\s+", outline[match.end():], flags=re.MULTILINE)
        end = match.end() + next_match.start() if next_match else len(outline)
        return outline[match.start():end]

    def _table_cells(self, line: str) -> list[str]:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            return []
        return [cell.strip() for cell in stripped.strip("|").split("|")]

    def _drawing_row_cells(self, line: str) -> list[str]:
        cells = self._table_cells(line)
        if cells:
            return cells
        stripped = line.strip()
        if "\t" in stripped:
            return [cell.strip() for cell in stripped.split("\t")]
        return []

    def _drawing_row_content(self, cells: list[str]) -> str:
        labels = ["图片编号", "对应 Topic", "页面短标题", "核心方案动作", "主视觉结构", "画面布局", "辅助短标签"]
        content = "\n".join(f"{label}：{value}" for label, value in zip(labels, cells[:7]) if value)
        return self._clean_drawing_content(content)

    def _drawing_style_lock(self, outline: str) -> str:
        section = self._drawing_plan_section(outline)
        if not section:
            return ""
        lines = []
        collecting = False
        for raw_line in section.splitlines():
            line = raw_line.strip()
            if line.startswith("|"):
                break
            if not line:
                continue
            if "统一风格锁定" in line:
                collecting = True
            if collecting:
                cleaned = line.lstrip(">").strip()
                if cleaned.rstrip("：:") == "统一风格锁定":
                    continue
                if cleaned:
                    lines.append(cleaned)
        return self._clean_drawing_content("\n".join(lines))

    def _merge_style_lock(self, base_style_lock: str, drawing_style_lock: str) -> str:
        if not drawing_style_lock:
            return base_style_lock
        return (
            f"{drawing_style_lock}\n\n"
            "以下为通用一致性约束，若与上方绘图风格锁定冲突，以上方绘图风格锁定为准：\n"
            f"{base_style_lock}"
        )

    def _drawing_content(self, page_script: str, fallback_section: str) -> str:
        content = page_script.strip() if page_script.strip() else fallback_section.strip()
        return self._clean_drawing_content(content)

    def _clean_drawing_content(self, content: str) -> str:
        blocked_headings = (
            "需要核验",
            "Needs verification",
            "Manual Verification",
            "风险提示",
            "Risk warning",
            "风险矩阵",
            "Risk Matrix",
            "信息来源",
            "Information sources",
            "证据地图",
            "Evidence Map",
            "下一步计划",
            "Next steps",
        )
        cleaned = []
        skipping = False
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if line.startswith("|"):
                cells = self._table_cells(line)
                if cells:
                    line_without_forbidden = " | ".join(cells[:7])
                    if any(key.lower() in line_without_forbidden.lower() for key in blocked_headings):
                        continue
                    cleaned.append(line_without_forbidden)
                    continue
            if any(key.lower() in line.lower() for key in blocked_headings):
                skipping = True
                continue
            if skipping and (line.startswith("* ") or line.startswith("- ") or re.match(r"^#{1,4}\s+", line) or "：" in line or ":" in line):
                skipping = False
            if skipping:
                continue
            if any(key.lower() in line.lower() for key in ("需核验", "needs verification", "risk warning", "信息来源", "下一步")):
                continue
            cleaned.append(raw_line)
        text = "\n".join(cleaned).strip()
        return text[:2400]

    def _section(self, outline: str, title: str) -> str:
        escaped_title = re.escape(title.strip())
        match = re.search(rf"^###\s+T?\d{{1,2}}[\.\s-]*{escaped_title}.*$", outline, flags=re.MULTILINE)
        if not match:
            match = re.search(rf"^###\s+.*{escaped_title}.*$", outline, flags=re.MULTILINE)
        if not match:
            return title
        pos = match.start()
        next_match = re.search(r"^###\s+", outline[match.end():], flags=re.MULTILINE)
        end = match.end() + next_match.start() if next_match else min(len(outline), pos + 2200)
        return outline[pos:end].strip()

    def _page_script_for(self, outline: str, index: int, topic_id: str) -> str:
        page_id = f"P{index:02d}"
        patterns = [
            rf"^\|\s*{page_id}\s*\|.*{topic_id}.*\|$",
            rf"^\|\s*{index:02d}\s*\|.*{topic_id}.*\|$",
            rf"^\|\s*{topic_id}\s*\|.*\|$",
        ]
        rows = []
        for pattern in patterns:
            rows.extend(re.findall(pattern, outline, flags=re.MULTILINE))
        return "\n".join(dict.fromkeys(row.strip() for row in rows))

    def _title_from_outline(self, outline: str) -> str:
        match = re.search(r"^#\s+(.+)$", outline, flags=re.MULTILINE)
        return match.group(1).strip() if match else ""

    def _size_for_aspect(self, aspect: str) -> str:
        if aspect in {"16:9", "wide", "landscape"}:
            return self.settings.default_image_size
        if aspect in {"4:3"}:
            return "1536x1152"
        if aspect in {"3:4"}:
            return "1152x1536"
        if aspect in {"1:1", "square"}:
            return "1024x1024"
        if aspect in {"9:16", "portrait"}:
            return "1024x1536"
        return self.settings.default_image_size

    def _image_size(self, requested_size: str | None, aspect: str) -> str:
        allowed = {
            "1024x1024",
            "1536x1024",
            "1024x1536",
            "2048x2048",
            "2048x1152",
            "3840x2160",
            "2160x3840",
        }
        if requested_size in allowed:
            return requested_size
        return self._size_for_aspect(aspect)

    def _mock_svg(self, idx: int, total: int, topic: str, title: str, instruction: str = "", version: int = 1) -> str:
        safe_topic = html.escape(topic[:80])
        safe_title = html.escape(title[:80])
        safe_instruction = html.escape(instruction[:80])
        return f"""<svg xmlns='http://www.w3.org/2000/svg' width='1536' height='1024' viewBox='0 0 1536 1024'>
  <defs>
    <linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='#08111f'/><stop offset='48%' stop-color='#1e1b4b'/><stop offset='100%' stop-color='#07111f'/></linearGradient>
    <linearGradient id='card' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='#ffffff' stop-opacity='.22'/><stop offset='100%' stop-color='#ffffff' stop-opacity='.07'/></linearGradient>
    <filter id='glow'><feGaussianBlur stdDeviation='14' result='blur'/><feMerge><feMergeNode in='blur'/><feMergeNode in='SourceGraphic'/></feMerge></filter>
  </defs>
  <rect width='1536' height='1024' fill='url(#bg)'/>
  <circle cx='220' cy='150' r='210' fill='#38bdf8' opacity='.18'/><circle cx='1300' cy='840' r='260' fill='#a78bfa' opacity='.22'/>
  <rect x='96' y='86' width='1344' height='852' rx='48' fill='url(#card)' stroke='rgba(255,255,255,.34)'/>
  <text x='150' y='155' fill='#93c5fd' font-size='24' font-family='Arial' font-weight='700'>Solution Agent · {idx:02d}/{total:02d} · v{version:02d}</text>
  <text x='150' y='220' fill='#ffffff' font-size='38' font-family='Arial' font-weight='800'>{safe_title}</text>
  <text x='150' y='298' fill='#ffffff' font-size='54' font-family='Arial' font-weight='900'>{safe_topic}</text>
  <g transform='translate(150 410)'><rect width='330' height='230' rx='32' fill='rgba(255,255,255,.10)' stroke='rgba(255,255,255,.22)'/><text x='34' y='70' fill='#dbeafe' font-size='28' font-family='Arial' font-weight='700'>输入与依据</text><text x='34' y='124' fill='#cbd5e1' font-size='21' font-family='Arial'>文档 · 政策 · 产业</text><text x='34' y='168' fill='#cbd5e1' font-size='21' font-family='Arial'>来源需要核验</text></g>
  <g transform='translate(604 360)' filter='url(#glow)'><rect width='330' height='330' rx='42' fill='rgba(56,189,248,.19)' stroke='rgba(125,211,252,.72)'/><text x='66' y='138' fill='#fff' font-size='38' font-family='Arial' font-weight='800'>Todo Agent</text><text x='66' y='190' fill='#dbeafe' font-size='23' font-family='Arial'>Research → Outline</text><text x='66' y='236' fill='#dbeafe' font-size='23' font-family='Arial'>Prompt → Images</text></g>
  <g transform='translate(1056 410)'><rect width='330' height='230' rx='32' fill='rgba(255,255,255,.10)' stroke='rgba(255,255,255,.22)'/><text x='34' y='70' fill='#dbeafe' font-size='28' font-family='Arial' font-weight='700'>输出与价值</text><text x='34' y='124' fill='#cbd5e1' font-size='21' font-family='Arial'>Markdown 大纲</text><text x='34' y='168' fill='#cbd5e1' font-size='21' font-family='Arial'>连续解决方案图</text></g>
  <path d='M505 525 C545 525 555 525 590 525' stroke='#7dd3fc' stroke-width='8' fill='none'/><path d='M950 525 C990 525 1000 525 1038 525' stroke='#7dd3fc' stroke-width='8' fill='none'/>
  <text x='150' y='842' fill='#c4b5fd' font-size='24' font-family='Arial'>{safe_instruction}</text>
</svg>"""
