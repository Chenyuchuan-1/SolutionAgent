from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.api.deps import agent, storage
from app.models.schemas import ImageEditRequest, ImageGenerateRequest

router = APIRouter()


@router.post("/images")
async def create_images(payload: ImageGenerateRequest):
    try:
        return await agent.generate_images(payload.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"图片生成失败：{exc}") from exc


@router.post("/image-edit")
async def edit_image(payload: ImageEditRequest):
    try:
        return await agent.edit_image(payload.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"图片修改失败：{exc}") from exc


@router.get("/runs/{run_id}/images/{filename}")
async def image_file(run_id: str, filename: str):
    path = storage.run_dir(run_id) / "images" / Path(filename).name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    media_type = "image/svg+xml" if path.suffix == ".svg" else "image/png"
    return FileResponse(path, media_type=media_type)
