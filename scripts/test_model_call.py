from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.models.openai_client import OpenAIClient, OpenAIClientError
from app.models.registry import get_model


def inspect_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        print("WARNING: .env file not found.")
        return
    seen: dict[str, int] = {}
    invalid_lines: list[int] = []
    duplicate_keys: list[str] = []
    for line_no, raw_line in enumerate(env_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            invalid_lines.append(line_no)
            continue
        key = line.split("=", 1)[0].strip()
        if key in seen:
            duplicate_keys.append(key)
        seen[key] = line_no
    if invalid_lines or duplicate_keys:
        print("== .env Warnings ==")
        if invalid_lines:
            print(f"Invalid non KEY=VALUE lines: {invalid_lines}")
        if duplicate_keys:
            print(f"Duplicate keys, later values win: {sorted(set(duplicate_keys))}")
        print()


def mask_secret(value: str) -> str:
    if not value:
        return "<empty>"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def print_config(include_image: bool) -> None:
    settings = get_settings()
    text_model = get_model("solution_planner")
    image_model = get_model("image_generator")
    print("== Runtime Config ==")
    print(f"OPENAI_API_KEY: {mask_secret(settings.openai_api_key)}")
    print(f"OPENAI_TEXT_MODEL: {text_model.model}")
    print(f"OPENAI_TEXT_URL: {settings.openai_text_url or '<SDK Responses API>'}")
    if include_image:
        print(f"OPENAI_IMAGE_MODEL: {image_model.model}")
        print(f"OPENAI_IMAGE_URL: {settings.openai_image_url or '<SDK Images API>'}")
        print(f"OPENAI_IMAGE_EDIT_URL: {settings.openai_image_edit_url or '<derived from image URL>'}")
        print(f"OPENAI_IMAGE_API_KEY: {mask_secret(settings.openai_image_api_key)}")
        print(f"OPENAI_IMAGE_AUTH_ENABLED: {settings.openai_image_auth_enabled}")
        print(f"OPENAI_IMAGE_INCLUDE_SIZE: {settings.openai_image_include_size}")
        print(f"DEFAULT_IMAGE_SIZE: {settings.default_image_size}")
        print(f"DEFAULT_IMAGE_QUALITY: {settings.default_image_quality}")
        print(f"IMAGE_GENERATION_CONCURRENCY: {settings.image_generation_concurrency}")
        print(f"REQUEST_TIMEOUT: {settings.request_timeout}s")
    print()


async def test_text_call(client: OpenAIClient, prompt: str) -> None:
    print("== Text Model Test ==")
    result = await client.generate_outline(
        system_prompt="You are a concise API smoke-test assistant. Reply with valid plain text only.",
        user_prompt=prompt,
    )
    if not result:
        raise OpenAIClientError("文本模型没有返回内容，请检查 OPENAI_API_KEY / OPENAI_TEXT_URL / OPENAI_TEXT_MODEL。")
    preview = result.strip().replace("\n", " ")[:800]
    print("Text call OK")
    print(f"Response preview: {preview}")
    print()


async def test_image_call(client: OpenAIClient, prompt: str, output_path: Path) -> None:
    settings = get_settings()
    print("== Image Model Test ==")
    data = await client.generate_image(
        prompt=prompt,
        size=settings.default_image_size,
        quality=settings.default_image_quality,
    )
    if not data:
        raise OpenAIClientError("图片模型没有返回图像数据，请检查 OPENAI_API_KEY / OPENAI_IMAGE_URL / OPENAI_IMAGE_MODEL。")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    print("Image call OK")
    print(f"Saved image: {output_path}")
    print(f"Bytes: {len(data)}")
    print()


async def main() -> int:
    parser = argparse.ArgumentParser(description="Test configured text and image model calls.")
    parser.add_argument(
        "--prompt",
        default="请用一句话回复：模型调用测试成功，并说明当前是文本模型连通性测试。",
        help="Prompt for the text model smoke test.",
    )
    parser.add_argument(
        "--image",
        action="store_true",
        help="Also test image generation. This may consume image-generation quota.",
    )
    parser.add_argument(
        "--skip-text",
        action="store_true",
        help="Skip the text model test. Useful when only OPENAI_IMAGE_API_KEY is configured.",
    )
    parser.add_argument(
        "--image-prompt",
        default=(
            "一张内容清晰的企业级解决方案信息图，用中文短标签展示：输入、调研、证据、方案、"
            "路线图、风险、验收指标。白色背景，专业咨询报告风格，信息丰富，不使用玻璃拟态。"
        ),
        help="Prompt for the image model smoke test.",
    )
    parser.add_argument(
        "--output",
        default="storage/test_model_call/image_test.png",
        help="Where to save the generated image when --image is used.",
    )
    args = parser.parse_args()

    settings = get_settings()
    inspect_env_file()
    print_config(include_image=args.image)
    if not args.skip_text and not settings.openai_api_key:
        print("ERROR: OPENAI_API_KEY is empty. Fill it in .env or pass --skip-text to test image only.", file=sys.stderr)
        return 2
    if args.image and settings.openai_image_auth_enabled and not (settings.openai_image_api_key or settings.openai_api_key):
        print("ERROR: Image auth is enabled, but both OPENAI_IMAGE_API_KEY and OPENAI_API_KEY are empty.", file=sys.stderr)
        return 2
    if args.image and not (settings.openai_image_url or settings.openai_api_key):
        print("ERROR: Image test needs OPENAI_IMAGE_URL or SDK image configuration.", file=sys.stderr)
        return 2

    client = OpenAIClient()
    try:
        if not args.skip_text:
            await test_text_call(client, args.prompt)
        if args.image:
            await test_image_call(client, args.image_prompt, ROOT / args.output)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("All requested model tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
