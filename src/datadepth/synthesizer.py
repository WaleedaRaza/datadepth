from __future__ import annotations

import json, random
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd


def _as_list(v: Any) -> List[str]:
    if not v:
        return []
    return [str(x[0]) if isinstance(v[0], list) else str(x) for x in v]


def _sample_numeric(c: Dict[str, Any], n: int) -> np.ndarray:
    low, high, mu = c["min"], c["max"], c["mean"]
    sigma = max((high - low) / 6, 1e-9)
    return np.clip(np.random.normal(mu, sigma, n), low, high)


def _sample_categorical(c: Dict[str, Any], n: int) -> List[str]:
    cats = _as_list(c.get("sample_values")) or [
        f"cat{i}" for i in range(c.get("unique", 5))
    ]
    return random.choices(cats, k=n)


def _sample_datetime(c: Dict[str, Any], n: int) -> List[str]:
    try:
        start, end = pd.to_datetime(c["min"]), pd.to_datetime(c["max"])
        return pd.date_range(start, end, periods=n).strftime("%Y-%m-%d").tolist()
    except Exception:
        return ["2000-01-01"] * n


def _sample_text(c: Dict[str, Any], n: int) -> List[str]:
    vals = _as_list(c.get("sample_values")) or ["lorem ipsum"]
    return random.choices(vals, k=n)


def generate_rows(schema: Dict[str, Any], rows: int = 1000) -> pd.DataFrame:
    cols = {}
    for col in schema["columns"]:
        kind = col["type"]
        if kind == "numeric":
            cols[col["name"]] = _sample_numeric(col, rows)
        elif kind == "datetime":
            cols[col["name"]] = _sample_datetime(col, rows)
        elif kind == "text":
            cols[col["name"]] = _sample_text(col, rows)
        else:
            cols[col["name"]] = _sample_categorical(col, rows)
    return pd.DataFrame(cols)


def generate_from_schema(p: Path | str, rows: int = 1000) -> pd.DataFrame:
    return generate_rows(json.loads(Path(p).read_text()), rows)


def save_rows(df: pd.DataFrame, out: Path | str) -> None:
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
