from typing import Any, Literal
from pydantic import BaseModel, Field


class RunCreateRequest(BaseModel):
    title: str = "未命名解决方案"


class OutlineRequest(BaseModel):
    run_id: str | None = None
    domain: str = ""
    goal: str = ""
    scenario: str = ""
    prompt: str = Field(default="", description="用户输入的文字型提示词")
    user_prompt: str | None = None
    topic_count: int = Field(default=8, ge=5, le=15)
    uploaded_files: list[str] = Field(default_factory=list)


class ImageGenerateRequest(BaseModel):
    run_id: str
    outline_markdown: str
    style_preset: str = "glass-card enterprise consulting diagram"
    aspect_ratio: str = "16:9"
    image_size: str = ""
    topic_count: int = Field(default=8, ge=5, le=15)


class ImageEditRequest(BaseModel):
    run_id: str
    image_id: str
    instruction: str


class RunStatus(BaseModel):
    run_id: str
    status: Literal["created", "running", "done", "failed"] = "created"
    stage: str = "created"
    progress: int = 0
    message: str = ""
    steps: list[dict[str, Any]] = Field(default_factory=list)
