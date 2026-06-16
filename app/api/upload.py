from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.deps import storage

router = APIRouter()


@router.post("/upload")
async def upload_files(run_id: str = Form(...), files: list[UploadFile] = File(...)):
    saved = []
    for file in files:
        try:
            saved.append(await storage.save_upload(run_id, file))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="Run not found") from exc
    return {"run_id": run_id, "saved": saved}
