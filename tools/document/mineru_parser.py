from __future__ import annotations

import asyncio
import io
import json
import re
import zipfile
from pathlib import Path
from typing import Any

import httpx

from app.core.config import get_settings


class MinerUParser:
    """MinerU 服务 API 适配器。"""

    supported_suffixes = {".pdf"}

    def __init__(self) -> None:
        self.settings = get_settings()

    async def parse(self, file_path: str) -> dict[str, Any]:
        path = Path(file_path)
        if path.suffix.lower() not in self.supported_suffixes:
            return {"file": str(path), "status": "skipped", "reason": "MinerU only handles PDF in this adapter"}
        if not self.settings.mineru_api_token:
            return {"file": str(path), "status": "failed", "type": "pdf", "title": path.stem, "error": "MINERU_API_TOKEN 未配置，无法调用 MinerU 服务 API。"}

        timeout = httpx.Timeout(self.settings.mineru_timeout)
        headers = {"Authorization": f"Bearer {self.settings.mineru_api_token}"}
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, trust_env=False) as client:
            batch_id, upload_url = await self._request_upload_url(client, headers, path)
            upload_response = await client.put(upload_url, content=path.read_bytes())
            upload_response.raise_for_status()
            result = await self._poll_batch_result(client, headers, batch_id, path.name)
            zip_url = result.get("full_zip_url")
            if not zip_url:
                raise RuntimeError(f"MinerU 解析完成但未返回 full_zip_url：{result}")
            parsed_zip = await self._download_and_parse_zip(client, zip_url)
        markdown = parsed_zip.get("markdown", "")
        content_list = parsed_zip.get("content_list", [])
        return {
            "file": str(path),
            "status": "parsed",
            "type": "pdf",
            "title": self._title(markdown, path.stem),
            "summary": self._summary(markdown),
            "chunks": self._chunks(markdown),
            "tables": self._tables(content_list),
            "figures": self._figures(content_list),
            "mineru": {
                "batch_id": batch_id,
                "data_id": result.get("data_id"),
                "state": result.get("state"),
                "full_zip_url": zip_url,
                "model_version": self.settings.mineru_model_version,
            },
        }

    async def _request_upload_url(self, client: httpx.AsyncClient, headers: dict[str, str], path: Path) -> tuple[str, str]:
        payload = {
            "files": [{"name": path.name, "data_id": self._data_id(path)}],
            "model_version": self.settings.mineru_model_version,
            "enable_formula": self.settings.mineru_enable_formula,
            "enable_table": self.settings.mineru_enable_table,
            "language": self.settings.mineru_language,
        }
        payload["files"][0]["is_ocr"] = self.settings.mineru_is_ocr
        response = await client.post(self._file_urls_url(), json=payload, headers={**headers, "Content-Type": "application/json"})
        data = self._json_response(response)
        batch_id = data.get("data", {}).get("batch_id")
        file_urls = data.get("data", {}).get("file_urls") or []
        if not batch_id or not file_urls:
            raise RuntimeError(f"MinerU 未返回 batch_id/file_urls：{data}")
        return batch_id, file_urls[0]

    async def _poll_batch_result(self, client: httpx.AsyncClient, headers: dict[str, str], batch_id: str, file_name: str) -> dict[str, Any]:
        deadline = asyncio.get_running_loop().time() + self.settings.mineru_timeout
        last_result: dict[str, Any] | None = None
        while asyncio.get_running_loop().time() < deadline:
            response = await client.get(self._batch_result_url(batch_id), headers=headers)
            data = self._json_response(response)
            results = data.get("data", {}).get("extract_result") or []
            result = next((item for item in results if item.get("file_name") == file_name), results[0] if results else {})
            last_result = result
            state = result.get("state")
            if state == "done":
                return result
            if state == "failed":
                raise RuntimeError(f"MinerU 解析失败：{result.get('err_msg') or result}")
            await asyncio.sleep(max(1.0, self.settings.mineru_poll_interval))
        raise TimeoutError(f"MinerU 解析超时，batch_id={batch_id}，最后状态：{last_result}")

    async def _download_and_parse_zip(self, client: httpx.AsyncClient, zip_url: str) -> dict[str, Any]:
        response = await client.get(zip_url)
        response.raise_for_status()
        markdown = ""
        content_list: list[dict[str, Any]] = []
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            for name in archive.namelist():
                lower_name = name.lower()
                if lower_name.endswith("full.md"):
                    markdown = archive.read(name).decode("utf-8", errors="ignore")
                elif lower_name.endswith("content_list.json") or lower_name.endswith("_content_list.json"):
                    content_list = json.loads(archive.read(name).decode("utf-8", errors="ignore"))
        return {"markdown": markdown, "content_list": content_list}

    def _json_response(self, response: httpx.Response) -> dict[str, Any]:
        if response.is_error:
            raise RuntimeError(f"MinerU HTTP {response.status_code}: {response.text[:500]}")
        data = response.json()
        if data.get("code") != 0:
            raise RuntimeError(f"MinerU API 错误：{data.get('msg') or data}")
        return data

    def _api_base(self) -> str:
        url = self.settings.mineru_mcp_url.rstrip("/")
        if url.endswith("/extract/task"):
            return url[: -len("/extract/task")]
        if "/api/v4/" in url:
            return url.split("/api/v4/", 1)[0].rstrip("/") + "/api/v4"
        return url

    def _file_urls_url(self) -> str:
        return f"{self._api_base()}/file-urls/batch"

    def _batch_result_url(self, batch_id: str) -> str:
        return f"{self._api_base()}/extract-results/batch/{batch_id}"

    def _data_id(self, path: Path) -> str:
        clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", path.stem).strip("._-")
        return (clean or "document")[:128]

    def _title(self, markdown: str, fallback: str) -> str:
        match = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
        return match.group(1).strip() if match else fallback

    def _summary(self, markdown: str) -> str:
        text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", markdown)
        text = re.sub(r"[#>*_`|~-]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:1200]

    def _chunks(self, markdown: str, size: int = 1200) -> list[dict[str, str]]:
        if not markdown.strip():
            return []
        sections = re.split(r"(?=^#{1,3}\s+)", markdown, flags=re.MULTILINE)
        chunks: list[dict[str, str]] = []
        for section in sections:
            text = section.strip()
            if not text:
                continue
            heading = text.splitlines()[0].lstrip("# ").strip()[:80] or f"chunk-{len(chunks) + 1}"
            for offset in range(0, min(len(text), 6000), size):
                chunks.append({"section": heading, "text": text[offset : offset + size]})
                if len(chunks) >= 12:
                    return chunks
        return chunks

    def _tables(self, content_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        tables = []
        for idx, item in enumerate(content_list, start=1):
            if item.get("type") != "table":
                continue
            tables.append({
                "index": idx,
                "caption": item.get("table_caption") or item.get("caption") or "",
                "html": item.get("table_body") or item.get("html") or "",
                "text": item.get("text") or "",
            })
        return tables[:20]

    def _figures(self, content_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        figures = []
        for idx, item in enumerate(content_list, start=1):
            if item.get("type") not in {"image", "figure"}:
                continue
            figures.append({
                "index": idx,
                "caption": item.get("img_caption") or item.get("caption") or "",
                "path": item.get("img_path") or item.get("image_path") or "",
            })
        return figures[:50]
