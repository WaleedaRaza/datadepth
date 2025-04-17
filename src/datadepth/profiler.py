import pandas as pd
from pathlib import Path
import json
from typing import Any, Dict

_NUMERIC = {"int64", "float64"}


def profile_csv(path: str | Path, sample: int | None = 50_000) -> Dict[str, Any]:
    df = pd.read_csv(path, nrows=sample)
    schema: dict[str, dict[str, Any]] = {}

    for col in df.columns:
        if str(df[col].dtype) in _NUMERIC:
            schema[col] = {
                "type": "number",
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
            }
        else:
            schema[col] = {
                "type": "categorical",
                "unique": int(df[col].nunique()),
                "sample_values": df[col].dropna().unique()[:5].tolist(),
            }

        if df[col].isna().any():
            schema[col]["nullable"] = True

    return {"columns": schema, "rows_scanned": len(df)}


def save_schema(schema: Dict[str, Any], out: str | Path = "schema.json") -> None:
    Path(out).write_text(json.dumps(schema, indent=2))
