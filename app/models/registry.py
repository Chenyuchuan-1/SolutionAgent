from dataclasses import dataclass
from typing import Literal

from app.core.config import get_settings

ModelCapability = Literal[
    "text", "vision", "tool_calling", "structured_output", "image_generation", "image_edit", "multi_turn_edit"
]


@dataclass(frozen=True)
class ModelSpec:
    role: str
    provider: str
    model: str
    capabilities: tuple[ModelCapability, ...]
    usage: str
    default_params: dict


def model_registry() -> dict[str, ModelSpec]:
    settings = get_settings()
    return {
        "solution_planner": ModelSpec(
            role="solution_planner",
            provider="openai",
            model=settings.openai_text_model,
            capabilities=("text", "vision", "tool_calling", "structured_output"),
            usage="需求拆解、todo 规划、资料综合、Markdown 大纲生成、图片脚本生成",
            default_params={"reasoning": {"effort": "high"}},
        ),
        "image_generator": ModelSpec(
            role="image_generator",
            provider="openai",
            model=settings.openai_image_model,
            capabilities=("image_generation",),
            usage="根据 topic prompt 生成解决方案图片",
            default_params={"size": settings.default_image_size, "quality": settings.default_image_quality},
        ),
        "image_editor": ModelSpec(
            role="image_editor",
            provider="openai",
            model=settings.openai_image_model,
            capabilities=("image_edit", "multi_turn_edit"),
            usage="用户针对单张图片进行对话式修改",
            default_params={"size": settings.default_image_size, "quality": settings.default_image_quality},
        ),
    }


def get_model(role: str) -> ModelSpec:
    registry = model_registry()
    if role not in registry:
        raise KeyError(f"Unknown model role: {role}")
    return registry[role]
