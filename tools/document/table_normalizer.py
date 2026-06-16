def normalize_table(rows: list[dict]) -> dict:
    columns = list(rows[0].keys()) if rows else []
    return {"columns": columns, "row_count_sample": len(rows), "sample_rows": rows[:20]}
