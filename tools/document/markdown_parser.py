from pathlib import Path


def parse_markdown(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    headings = [line.strip("# ") for line in text.splitlines() if line.startswith("#")]
    return {"file": path, "type": "markdown", "headings": headings, "text": text}
