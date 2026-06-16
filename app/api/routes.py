from fastapi import APIRouter

from app.api.history import router as history_router
from app.api.images import router as images_router
from app.api.exports import router as exports_router
from app.api.outline import router as outline_router
from app.api.upload import router as upload_router
from app.models.schemas import RunCreateRequest
from app.api.deps import agent

router = APIRouter(prefix="/api")
router.include_router(upload_router)
router.include_router(outline_router)
router.include_router(images_router)
router.include_router(exports_router)
router.include_router(history_router)


@router.post("/runs")
async def create_run(payload: RunCreateRequest):
    return await agent.create_run(payload.title)


@router.get("/runs/{run_id}/status")
async def run_status(run_id: str):
    return agent.status(run_id)
