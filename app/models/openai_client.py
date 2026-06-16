from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path
from typing import Any

import httpx
from openai import AsyncOpenAI, OpenAIError

from app.core.config import get_settings
from app.models.registry import get_model


class OpenAIClientError(RuntimeError):
    pass


class OpenAIClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = (
            AsyncOpenAI(
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url or None,
            )
            if self.settings.openai_api_key
            else None
        )

    @property
    def enabled(self) -> bool:
        return self._client is not None

    async def generate_outline(self, system_prompt: str, user_prompt: str) -> str | None:
        if not self.settings.openai_api_key:
            return None
        model = get_model("solution_planner")
        try:
            if self.settings.openai_text_url:
                return await self._generate_outline_with_text_url(model.model, system_prompt, user_prompt)
            if not self._client:
                return None
            response = await self._client.responses.create(
                model=model.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return getattr(response, "output_text", None) or str(response)
        except OpenAIError as exc:
            raise OpenAIClientError(self._friendly_error(exc)) from exc
        except OpenAIClientError:
            raise
        except httpx.HTTPError as exc:
            raise OpenAIClientError(self._friendly_error(exc)) from exc

    async def summarize_with_deepseek(self, system_prompt: str, user_prompt: str) -> str | None:
        if not self.settings.openai_api_key:
            return None
        payload = {
            "model": self.settings.deepseek_summary_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }
        try:
            data = await self._post_json(self._completion_url(self.settings.deepseek_summary_base_url), payload, auth_enabled=True)
            if data.get("choices"):
                message = data["choices"][0].get("message", {})
                content = message.get("content")
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    return "".join(part.get("text", "") for part in content if isinstance(part, dict))
            return data.get("output_text") or str(data)
        except OpenAIClientError:
            raise
        except httpx.HTTPError as exc:
            raise OpenAIClientError(self._friendly_error(exc)) from exc

    async def generate_image(self, prompt: str, size: str, quality: str) -> bytes | None:
        if not self.settings.openai_image_url and not self.settings.openai_api_key:
            return None
        model = get_model("image_generator")
        try:
            if self.settings.openai_image_url:
                return await self._generate_image_with_image_url(model.model, prompt, size, quality)
            if not self._client:
                return None
            response = await self._client.images.generate(model=model.model, prompt=prompt, size=size, quality=quality, n=1)
            item = response.data[0]
            b64 = getattr(item, "b64_json", None)
            if b64:
                return base64.b64decode(b64)
            raise OpenAIClientError("图片模型未返回 base64 图像数据")
        except OpenAIError as exc:
            raise OpenAIClientError(self._friendly_error(exc)) from exc
        except OpenAIClientError:
            raise
        except httpx.HTTPError as exc:
            raise OpenAIClientError(self._friendly_error(exc)) from exc

    async def edit_image(self, prompt: str, image_path: Path, size: str, quality: str) -> bytes | None:
        if not (self.settings.openai_image_edit_url or self.settings.openai_image_url) and not self.settings.openai_api_key:
            return None
        model = get_model("image_editor")
        try:
            if self.settings.openai_image_edit_url or self.settings.openai_image_url:
                return await self._edit_image_with_image_url(model.model, prompt, image_path, size, quality)
            if not self._client:
                return None
            with image_path.open("rb") as image_file:
                response = await self._client.images.edit(model=model.model, image=image_file, prompt=prompt, size=size, n=1)
            return await self._image_bytes_from_sdk_response(response)
        except OpenAIError as exc:
            raise OpenAIClientError(self._friendly_error(exc)) from exc
        except OpenAIClientError:
            raise
        except httpx.HTTPError as exc:
            raise OpenAIClientError(self._friendly_error(exc)) from exc

    async def _generate_outline_with_text_url(self, model: str, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        data = await self._post_json(self._completion_url(self.settings.openai_text_url), payload, auth_enabled=True)
        if data.get("choices"):
            message = data["choices"][0].get("message", {})
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "".join(part.get("text", "") for part in content if isinstance(part, dict))
        if data.get("output_text"):
            return str(data["output_text"])
        if data.get("output"):
            return str(data["output"])
        return str(data)

    async def _generate_image_with_image_url(self, model: str, prompt: str, size: str, quality: str) -> bytes:
        payload = {
            "model": model,
            "prompt": prompt,
            "quality": quality,
            "n": 1,
        }
        if self.settings.openai_image_include_size or size:
            payload["size"] = size
        if self.settings.openai_image_response_format:
            payload["response_format"] = self.settings.openai_image_response_format
        data = await self._post_json(
            self._image_generation_url(self.settings.openai_image_url),
            payload,
            auth_enabled=self.settings.openai_image_auth_enabled,
            api_key=self.settings.openai_image_api_key or self.settings.openai_api_key,
        )
        item = (data.get("data") or [{}])[0]
        return await self._image_bytes_from_item(item)

    async def _edit_image_with_image_url(self, model: str, prompt: str, image_path: Path, size: str, quality: str) -> bytes:
        data = {
            "model": model,
            "prompt": prompt,
            "quality": quality,
            "n": "1",
        }
        if self.settings.openai_image_include_size or size:
            data["size"] = size
        if self.settings.openai_image_response_format:
            data["response_format"] = self.settings.openai_image_response_format
        mime_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
        files = {"image": (image_path.name, image_path.read_bytes(), mime_type)}
        response_data = await self._post_multipart(
            self._image_edit_url(self.settings.openai_image_edit_url or self.settings.openai_image_url),
            data,
            files,
            auth_enabled=self.settings.openai_image_auth_enabled,
            api_key=self.settings.openai_image_api_key or self.settings.openai_api_key,
        )
        item = (response_data.get("data") or [{}])[0]
        return await self._image_bytes_from_item(item)

    async def _image_bytes_from_sdk_response(self, response: Any) -> bytes:
        item = response.data[0]
        b64 = getattr(item, "b64_json", None)
        if b64:
            return base64.b64decode(b64)
        image_url = getattr(item, "url", None)
        if image_url:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout, follow_redirects=True, trust_env=False) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                return response.content
        raise OpenAIClientError("图片编辑模型未返回 b64_json 或 url 图像数据")

    async def _image_bytes_from_item(self, item: dict[str, Any]) -> bytes:
        b64 = item.get("b64_json") or item.get("base64") or item.get("image_base64")
        if b64:
            return base64.b64decode(b64)
        image_url = item.get("url")
        if image_url:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout, follow_redirects=True, trust_env=False) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                return response.content
        raise OpenAIClientError("图片模型未返回 b64_json 或 url 图像数据")

    async def _post_json(self, url: str, payload: dict[str, Any], auth_enabled: bool = True, api_key: str | None = None) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if auth_enabled:
            token = api_key if api_key is not None else self.settings.openai_api_key
            if token:
                headers["Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient(timeout=self.settings.request_timeout, follow_redirects=True, trust_env=False) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.is_error:
                body = response.text[:1000].replace("\n", " ")
                raise OpenAIClientError(f"HTTP {response.status_code} from {url}: {body}")
            try:
                return response.json()
            except json.JSONDecodeError as exc:
                body = response.text[:1000].replace("\n", " ")
                raise OpenAIClientError(f"接口返回的不是 JSON：{body}") from exc

    async def _post_multipart(
        self,
        url: str,
        data: dict[str, str],
        files: dict[str, tuple[str, bytes, str]],
        auth_enabled: bool = True,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        headers = {}
        if auth_enabled:
            token = api_key if api_key is not None else self.settings.openai_api_key
            if token:
                headers["Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient(timeout=self.settings.request_timeout, follow_redirects=True, trust_env=False) as client:
            response = await client.post(url, data=data, files=files, headers=headers)
            if response.is_error:
                body = response.text[:1000].replace("\n", " ")
                raise OpenAIClientError(f"HTTP {response.status_code} from {url}: {body}")
            try:
                return response.json()
            except json.JSONDecodeError as exc:
                body = response.text[:1000].replace("\n", " ")
                raise OpenAIClientError(f"接口返回的不是 JSON：{body}") from exc

    def _completion_url(self, url: str) -> str:
        clean = url.rstrip("/")
        if clean.endswith("/chat/completions"):
            return clean
        return f"{clean}/chat/completions"

    def _image_generation_url(self, url: str) -> str:
        clean = url.rstrip("/")
        if clean.endswith("/images/generations"):
            return clean
        return f"{clean}/images/generations"

    def _image_edit_url(self, url: str) -> str:
        clean = url.rstrip("/")
        if clean.endswith("/images/edits"):
            return clean
        if clean.endswith("/images/generations"):
            return f"{clean[: -len('/images/generations')]}/images/edits"
        return f"{clean}/images/edits"

    def _friendly_error(self, exc: Exception) -> str:
        message = str(exc) or exc.__class__.__name__
        lower = message.lower()
        if "api key" in lower or "authentication" in lower:
            return "OpenAI API key 缺失或无效，请检查 OPENAI_API_KEY。"
        if "rate" in lower or "quota" in lower:
            return "OpenAI 调用达到限速或额度不足，请稍后重试。"
        if "timed out" in lower or "readtimeout" in lower:
            return f"OpenAI 图片/文本接口响应超时，请检查服务端生成耗时，或调大 REQUEST_TIMEOUT（当前 {self.settings.request_timeout}s）。"
        if "401" in lower or "unauthorized" in lower:
            return "OpenAI 接口鉴权失败，请检查 OPENAI_API_KEY、OPENAI_IMAGE_API_KEY 和 OPENAI_IMAGE_AUTH_ENABLED。"
        if "404" in lower:
            return "OpenAI URL 不可用，请检查 OPENAI_TEXT_URL 或 OPENAI_IMAGE_URL 是否应为 /v1 或完整 endpoint。"
        return f"OpenAI API 调用失败（{exc.__class__.__name__}）：{message[:500]}"
