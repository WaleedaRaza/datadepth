# src/datadepth/profiler.py
"""
Light‑weight CSV → schema profiler for DataDepth v1.x

Call profile_csv(path) → dict  ➜  dump with save_schema(schema, out_path)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
_METADATA_TOKENS = {"ticker", "date", "nan", ""}


def _looks_like_header(row: pd.Series, column_names: List[str]) -> bool:
    """True if row‑values == column names OR all‐text w/ no digits."""
    row_str = row.astype(str).str.lower()
    # matches own column names?
    if list(row_str) == [c.lower() for c in column_names]:
        return True
    # row is all alphabetic tokens (metadata)?
    if row_str.str.fullmatch(r"[a-z_]+").all():
        return True
    return False


def _infer_col_type(s: pd.Series) -> str:
    """Return one of numeric|datetime|categorical|text."""
    s_nonan = s.dropna()
    if s_nonan.empty:
        return "text"

    # Numeric?
    try:
        pd.to_numeric(s_nonan.sample(min(20, len(s_nonan)), random_state=42))
        return "numeric"
    except Exception:
        pass

    # Datetime?
    dt = pd.to_datetime(
        s_nonan.sample(min(20, len(s_nonan)), random_state=42), errors="coerce"
    )
    if dt.notna().mean() > 0.8:
        return "datetime"

    # Categorical or free text
    unique_ratio = s_nonan.nunique() / len(s_nonan)
    return "categorical" if unique_ratio < 0.4 else "text"


# --------------------------------------------------------------------------- #
# Profiling core                                                              #
# --------------------------------------------------------------------------- #
class Profiler:
    def __init__(self, df: pd.DataFrame):
        self.df = self._clean(df)

    # ---------- cleaning --------------------------------------------------- #
    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        # 1. drop fully‑empty rows
        df = df.dropna(how="all")

        # 2. drop obvious metadata rows
        df = df[
            ~df.apply(
                lambda r: _looks_like_header(r, df.columns.tolist())
                or r.astype(str).str.lower().isin(_METADATA_TOKENS).all(),
                axis=1,
            )
        ]

        return df.reset_index(drop=True)

    # ---------- per‑column stats ------------------------------------------ #
    def _profile_column(self, col: str) -> Dict[str, Any]:
        s = self.df[col]
        col_type = _infer_col_type(s)
        out: Dict[str, Any] = {
            "name": col,
            "type": col_type,
            "nullable": bool(s.isnull().any()),
        }

        if col_type == "numeric":
            s_num = pd.to_numeric(s, errors="coerce")
            out.update(
                mean=float(s_num.mean()),
                std=float(s_num.std(ddof=0)),
                min=float(s_num.min()),
                max=float(s_num.max()),
            )
        elif col_type == "categorical":
            vc = s.value_counts(dropna=True)
            out.update(
                unique=int(vc.size),
                sample_values=[[k, float(vc[k] / len(s))] for k in vc.head(20).index],
            )
        elif col_type == "datetime":
            s_dt = pd.to_datetime(s, errors="coerce")
            out.update(min=str(s_dt.min().date()), max=str(s_dt.max().date()))

        # text → no extra stats for now
        return out

    # ---------- public API ------------------------------------------------- #
    def profile(self) -> Dict[str, Any]:
        return {
            "columns": [self._profile_column(c) for c in self.df.columns],
            "num_rows": int(len(self.df)),
        }


# --------------------------------------------------------------------------- #
# Top‑level convenience wrappers                                              #
# --------------------------------------------------------------------------- #
def _read_csv_safely(path: str | Path) -> pd.DataFrame:
    """
    Try to read a CSV that *may* not have a header row.
    1st attempt: header=0
    If first row comes out numeric‑ish, re‑read with header=None.
    """
    df = pd.read_csv(path, low_memory=False)

    # Heuristic: >60 % of first row cells parse as numbers → treat as data
    first = df.iloc[0].astype(str)
    numericish = pd.to_numeric(first, errors="coerce").notna().mean() > 0.6
    if numericish:
        df = pd.read_csv(path, header=None, low_memory=False)
        df.columns = [f"col_{i}" for i in range(df.shape[1])]

    return df


# ── Replace the old profile_csv with this version ──────────────────────────────
def profile_csv(path: str, *, force_no_header: bool = False) -> dict:
    """
    Read a CSV, auto‑detect headers unless force_no_header=True,
    return an inferred schema dict.
    """
    if force_no_header:
        # First row is data, so read without a header and create default col names
        df = pd.read_csv(path, header=None)
        df.columns = [f"col_{i}" for i in range(df.shape[1])]
    else:
        # Try header=0, but if the first row looks numeric we’ll re‑read w/out header
        df = pd.read_csv(path, header=0)
        # Heuristic: if **all** values in first row parse as numbers/dates, it’s data
        first_row = df.iloc[0]
        looks_numeric = pd.to_numeric(first_row, errors="coerce").notna().all()
        looks_date = pd.to_datetime(first_row, errors="coerce").notna().all()
        if looks_numeric or looks_date:
            df = pd.read_csv(path, header=None)
            df.columns = [f"col_{i}" for i in range(df.shape[1])]

    # Hand the cleaned dataframe to the existing Profiler class
    return Profiler(df).profile()


def save_schema(profile: Dict[str, Any], out_path: str | Path = "schema.json") -> None:
    """Dump schema to disk (always JSON‑serialisable)."""
    clean = json.loads(json.dumps(profile, default=str))
    Path(out_path).write_text(json.dumps(clean, indent=2))


# --------------------------------------------------------------------------- #
# CLI quick‑test
# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # python -m datadepth.profiler file.csv
    import sys

    schema = profile_csv(sys.argv[1])
    save_schema(schema, "schema.json")
    print("✅ schema.json written")
