# src/datadepth/validators.py
import json
from pathlib import Path


def load_schema(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def validate_schema(s: dict) -> None:
    if "columns" not in s:
        raise ValueError("Schema missing 'columns'.")
    for col in s["columns"]:
        if not {"name", "type"} <= col.keys():
            raise ValueError(f"Bad column entry: {col}")
