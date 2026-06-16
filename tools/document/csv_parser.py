import csv
from pathlib import Path


def parse_csv(path: str, limit: int = 20) -> dict:
    with Path(path).open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        rows = [row for _, row in zip(range(limit), reader)]
        return {"file": path, "type": "csv", "columns": reader.fieldnames or [], "sample_rows": rows}
