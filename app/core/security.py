from pathlib import Path
from uuid import uuid4

ALLOWED_UPLOAD_SUFFIXES = {".pdf", ".doc", ".docx", ".md", ".markdown", ".csv", ".xls", ".xlsx", ".txt"}


def safe_filename(filename: str) -> str:
    stem = Path(filename or "upload.bin").stem.replace(" ", "_")[:80] or "upload"
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_UPLOAD_SUFFIXES:
        raise ValueError(f"不支持的文件类型：{suffix or 'unknown'}")
    clean = "".join(ch for ch in stem if ch.isalnum() or ch in {"-", "_", "."}) or "upload"
    return f"{clean}-{uuid4().hex[:8]}{suffix}"


def validate_run_id(run_id: str) -> str:
    if not run_id or any(part in run_id for part in ("..", "/", "\\")):
        raise ValueError("Invalid run_id")
    return run_id
