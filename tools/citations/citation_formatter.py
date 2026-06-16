def markdown_link_source(source: dict) -> str:
    title = source.get("title") or "source"
    url = source.get("url") or "#"
    date = source.get("published_date") or "日期待核验"
    return f"[{title}]({url})（{source.get('source_type', 'webpage')}，{date}）"
