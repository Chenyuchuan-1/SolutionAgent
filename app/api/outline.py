from fastapi import APIRouter, HTTPException

from app.api.deps import agent
from app.models.schemas import OutlineRequest

router = APIRouter()


@router.post("/outline")
async def create_outline(payload: OutlineRequest):
    try:
        data = payload.model_dump()
        if data.get("user_prompt") and not data.get("prompt"):
            data["prompt"] = data["user_prompt"]
        return await agent.generate_outline(data)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"大纲生成失败：{exc}") from exc
