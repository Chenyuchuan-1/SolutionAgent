from __future__ import annotations

import html
import io
import mimetypes
import re
import zipfile
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response, StreamingResponse

from app.api.deps import storage

router = APIRouter()


@router.get("/runs/{run_id}/outline.md")
async def download_outline_markdown(run_id: str):
    meta = _load_run(run_id)
    markdown = meta.get("outline_markdown") or ""
    if not markdown:
        raise HTTPException(status_code=404, detail="Outline not found")
    filename = _download_name(meta, "outline.md")
    return Response(
        markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": _content_disposition(filename)},
    )


@router.get("/runs/{run_id}/outline.html")
async def download_outline_html(run_id: str):
    meta = _load_run(run_id)
    markdown = meta.get("outline_markdown") or ""
    if not markdown:
        raise HTTPException(status_code=404, detail="Outline not found")
    filename = _download_name(meta, "outline.html")
    document = _html_document(meta.get("title") or "Solution Outline", markdown)
    return Response(
        document,
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": _content_disposition(filename)},
    )


@router.get("/runs/{run_id}/images/{filename}/download")
async def download_image(run_id: str, filename: str):
    path = storage.run_dir(run_id) / "images" / Path(filename).name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return FileResponse(path, media_type=media_type, filename=path.name)


@router.get("/runs/{run_id}/images.zip")
async def download_all_images(run_id: str):
    meta = _load_run(run_id)
    image_dir = storage.run_dir(run_id) / "images"
    files = []
    for item in meta.get("images", []):
        filename = Path(item.get("filename", "")).name
        path = image_dir / filename
        if filename and path.exists():
            files.append(path)
    if not files and image_dir.exists():
        files = sorted(path for path in image_dir.iterdir() if path.is_file())
    if not files:
        raise HTTPException(status_code=404, detail="Images not found")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, arcname=path.name)
    buffer.seek(0)
    filename = _download_name(meta, "images.zip")
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": _content_disposition(filename)},
    )


def _load_run(run_id: str) -> dict:
    try:
        return storage.load_run(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc


def _download_name(meta: dict, suffix: str) -> str:
    title = meta.get("title") or meta.get("run_id") or "solution"
    safe = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff_.-]+", "_", title).strip("._-")
    return f"{safe or 'solution'}_{suffix}"


def _content_disposition(filename: str) -> str:
    quoted = quote(filename)
    return f"attachment; filename*=UTF-8''{quoted}"


def _html_document(title: str, markdown: str) -> str:
    body = _markdown_to_html(markdown)
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe_title}</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #0f172a; background: #f8fafc; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 48px 28px; }}
    article {{ background: white; border: 1px solid #e2e8f0; border-radius: 24px; padding: 34px; box-shadow: 0 20px 70px rgba(15, 23, 42, 0.08); }}
    h1, h2, h3 {{ line-height: 1.25; color: #0f172a; }}
    h1 {{ font-size: 32px; margin-top: 0; }}
    h2 {{ margin-top: 34px; padding-top: 18px; border-top: 1px solid #e2e8f0; }}
    p, li {{ line-height: 1.75; }}
    table {{ width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 14px; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 10px 12px; vertical-align: top; }}
    th {{ background: #f1f5f9; }}
    code {{ background: #f1f5f9; padding: 2px 5px; border-radius: 6px; }}
    a {{ color: #0284c7; }}
  </style>
</head>
<body>
  <main><article>{body}</article></main>
</body>
</html>"""


def _markdown_to_html(markdown: str) -> str:
    blocks = []
    paragraph = []
    list_items = []
    lines = markdown.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        if not line:
            _flush_paragraph(blocks, paragraph)
            _flush_list(blocks, list_items)
            index += 1
            continue
        if line.startswith("|") and index + 1 < len(lines) and lines[index + 1].strip().startswith("|"):
            _flush_paragraph(blocks, paragraph)
            _flush_list(blocks, list_items)
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            blocks.append(_table_to_html(table_lines))
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            _flush_paragraph(blocks, paragraph)
            _flush_list(blocks, list_items)
            level = min(len(heading.group(1)), 3)
            blocks.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
        elif re.match(r"^[-*]\s+", line):
            _flush_paragraph(blocks, paragraph)
            list_items.append(re.sub(r"^[-*]\s+", "", line))
        else:
            paragraph.append(line)
        index += 1
    _flush_paragraph(blocks, paragraph)
    _flush_list(blocks, list_items)
    return "\n".join(blocks)


def _flush_paragraph(blocks: list[str], paragraph: list[str]) -> None:
    if paragraph:
        blocks.append(f"<p>{_inline(' '.join(paragraph))}</p>")
        paragraph.clear()


def _flush_list(blocks: list[str], items: list[str]) -> None:
    if items:
        blocks.append("<ul>" + "".join(f"<li>{_inline(item)}</li>" for item in items) + "</ul>")
        items.clear()


def _table_to_html(lines: list[str]) -> str:
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in rows[1]):
        rows.pop(1)
    if not rows:
        return ""
    header = "".join(f"<th>{_inline(cell)}</th>" for cell in rows[0])
    body = "".join("<tr>" + "".join(f"<td>{_inline(cell)}</td>" for cell in row) + "</tr>" for row in rows[1:])
    return f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"


def _inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped
