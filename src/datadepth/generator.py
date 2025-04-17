from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd


def _sample_numeric(col_schema: Dict[str, Any], n: int) -> np.ndarray:
    low = col_schema["min"]
    high = col_schema["max"]
    mean = col_schema["mean"]
    sigma = max((high - low) / 6, 1e-9)
    values = np.random.normal(loc=mean, scale=sigma, size=n)
    return np.clip(values, low, high)


def _sample_categorical(col_schema: Dict[str, Any], n: int) -> list[str]:
    cats = col_schema.get("sample_values", [])
    if not cats:
        cats = [f"cat{i}" for i in range(col_schema.get("unique", 1))]
    probs = [1 / len(cats)] * len(cats)
    return random.choices(cats, probs, k=n)


def _sample_datetime(col_schema: Dict[str, Any], n: int) -> list[str]:
    start = pd.to_datetime(col_schema["min"])
    end = pd.to_datetime(col_schema["max"])
    dates = pd.date_range(start=start, end=end, periods=n)
    return dates.strftime("%Y-%m-%d").tolist()


def generate_from_schema(schema_path: str | Path, rows: int = 1000) -> pd.DataFrame:
    meta = json.loads(Path(schema_path).read_text())
    columns = meta["columns"]
    output = {}

    for col_schema in columns:
        col_name = col_schema["name"]
        col_type = col_schema["type"]

        if col_type == "numeric":
            output[col_name] = _sample_numeric(col_schema, rows)
        elif col_type == "datetime":
            output[col_name] = _sample_datetime(col_schema, rows)
        else:
            output[col_name] = _sample_categorical(col_schema, rows)

    return pd.DataFrame(output)


def save_df(df: pd.DataFrame, out_path: str | Path) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
