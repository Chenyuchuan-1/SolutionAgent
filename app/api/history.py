from fastapi import APIRouter, HTTPException

from app.api.deps import storage

router = APIRouter()


@router.get("/history")
async def list_history():
    return {"items": storage.list_runs()}


@router.get("/history/{run_id}")
async def get_history(run_id: str):
    try:
        return storage.load_run(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc
