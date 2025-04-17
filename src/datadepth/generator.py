from __future__ import annotations
import json, random, math
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict, Any

def _sample_numeric(col_schema: Dict[str, Any], n: int) -> np.ndarray:
    low, high = col_schema["min"], col_schema["max"]
    mean = col_schema["mean"]
    # crude stdev guess
    sigma = max((high - low) / 6, 1e-9)
    values = np.random.normal(mean, sigma, n)
    return np.clip(values, low, high)

def _sample_categorical(col_schema: Dict[str, Any], n: int) -> list[str]:
    cats = col_schema["sample_values"]
    if not cats:
        cats = [f"cat{i}" for i in range(col_schema["unique"] or 1)]
    probs = [1 / len(cats)] * len(cats)
    return random.choices(cats, probs, k=n)

def generate_from_schema(schema_path: str | Path, rows: int = 1000) -> pd.DataFrame:
    meta = json.loads(Path(schema_path).read_text())
    cols_out: dict[str, Any] = {}

    for col, col_schema in meta["columns"].items():
        if col_schema["type"] == "number":
            cols_out[col] = _sample_numeric(col_schema, rows)
        else:
            cols_out[col] = _sample_categorical(col_schema, rows)

    return pd.DataFrame(cols_out)

def save_df(df: pd.DataFrame, out_path: str | Path) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
