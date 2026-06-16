from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.security import safe_filename, validate_run_id


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class RunStorage:
    def __init__(self) -> None:
        self.root = get_settings().storage_root
        self.root.mkdir(parents=True, exist_ok=True)

    def run_dir(self, run_id: str) -> Path:
        return self.root / validate_run_id(run_id)

    def ensure_run_dirs(self, run_id: str) -> Path:
        run_dir = self.run_dir(run_id)
        for child in ["input", "uploads", "parsed", "retrieval", "outline/outline_versions", "prompts", "images", "edits"]:
            (run_dir / child).mkdir(parents=True, exist_ok=True)
        return run_dir

    def create_run(self, title: str = "未命名解决方案", user_input: dict[str, Any] | None = None) -> dict[str, Any]:
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid4().hex[:8]
        self.ensure_run_dirs(run_id)
        meta = {
            "run_id": run_id,
            "title": title,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "domain": "",
            "goal": "",
            "scenario": "",
            "topic_count": 8,
            "user_input": user_input or {},
            "outline_markdown": "",
            "topics": [],
            "images": [],
            "retrieval_sources": [],
            "uploaded_files": [],
            "edit_history": [],
            "todos": [],
            "status": {"status": "created", "stage": "created", "progress": 0, "message": "Run 已创建", "steps": []},
        }
        self.save_run(meta)
        return meta

    def save_run(self, meta: dict[str, Any]) -> None:
        meta["updated_at"] = now_iso()
        run_dir = self.ensure_run_dirs(meta["run_id"])
        (run_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_run(self, run_id: str) -> dict[str, Any]:
        path = self.run_dir(run_id) / "meta.json"
        if not path.exists():
            raise FileNotFoundError(run_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def list_runs(self) -> list[dict[str, Any]]:
        items = []
        for meta_file in sorted(self.root.glob("*/meta.json"), reverse=True):
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                items.append({
                    "run_id": meta.get("run_id"),
                    "title": meta.get("title"),
                    "created_at": meta.get("created_at"),
                    "updated_at": meta.get("updated_at"),
                    "domain": meta.get("domain"),
                    "user_input": meta.get("user_input", {}),
                    "images": meta.get("images", []),
                    "topic_count": meta.get("topic_count"),
                    "outline_markdown": meta.get("outline_markdown", ""),
                })
            except Exception:
                continue
        return items

    async def save_upload(self, run_id: str, upload: UploadFile) -> dict[str, Any]:
        run_dir = self.ensure_run_dirs(run_id)
        safe_name = safe_filename(upload.filename or "upload.bin")
        target = run_dir / "uploads" / safe_name
        with target.open("wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)
        meta = self.load_run(run_id)
        record = {"name": upload.filename, "stored_name": safe_name, "path": str(target), "size": target.stat().st_size, "content_type": upload.content_type}
        meta.setdefault("uploaded_files", []).append(record)
        self.save_json(run_id, "input/uploaded_files.json", meta["uploaded_files"])
        self.save_run(meta)
        return record

    def save_json(self, run_id: str, relative_path: str, data: Any) -> Path:
        path = self.run_dir(run_id) / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def save_text(self, run_id: str, relative_path: str, text: str) -> Path:
        path = self.run_dir(run_id) / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def save_bytes(self, run_id: str, relative_path: str, data: bytes) -> Path:
        path = self.run_dir(run_id) / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def update_status(self, run_id: str, stage: str, progress: int, message: str, status: str = "running") -> dict[str, Any]:
        meta = self.load_run(run_id)
        step = {"stage": stage, "progress": progress, "message": message, "at": now_iso()}
        current = meta.setdefault("status", {})
        current.update({"status": status, "stage": stage, "progress": progress, "message": message})
        current.setdefault("steps", []).append(step)
        self.save_run(meta)
        return current

    def public_image_url(self, run_id: str, filename: str) -> str:
        return f"/api/runs/{run_id}/images/{filename}"
