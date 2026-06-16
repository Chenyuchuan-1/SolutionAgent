from pathlib import Path


def parse_word(path: str) -> dict:
    try:
        import docx
        document = docx.Document(path)
        text = "\n".join(p.text for p in document.paragraphs)
    except Exception as exc:
        return {"file": path, "type": "word", "status": "failed", "error": str(exc)}
    return {"file": path, "type": "word", "text": text, "title": Path(path).stem}
