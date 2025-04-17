# ───────────────────────────────── src/datadepth/cli.py ──────────────────────
"""DataDepth command‑line interface.

$ datadepth --help
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click
import pandas as pd

from .profiler import profile_csv, save_schema
from .synthesizer import generate_rows, save_rows
from .validators import load_schema, validate_schema


# ---------------------------------------------------------------------------- #
# Root group                                                                   #
# ---------------------------------------------------------------------------- #
@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(package_name="datadepth", prog_name="datadepth")
def cli() -> None:
    """Synthetic data Swiss‑army knife.

    • Create a **schema** from any CSV
    • Generate realistic **synthetic rows** from that schema
    • Validate an existing schema file
    """


# ---------------------------------------------------------------------------- #
# 1. profile                                                                   #
# ---------------------------------------------------------------------------- #
@cli.command("profile")
@click.argument("input_csv", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-s",
    "--schema-out",
    default="schema.json",
    show_default=True,
    help="Path to save generated schema",
)
@click.option(
    "--no-header",
    is_flag=True,
    help="Force read CSV as *headerless* even if the first row looks textual.",
)
def profile_cmd(input_csv: str, schema_out: str, no_header: bool) -> None:
    """Infer schema from INPUT_CSV and write JSON to --schema-out."""
    schema = profile_csv(input_csv, force_no_header=no_header)
    save_schema(schema, schema_out)
    click.echo(f"✅  Schema saved → {schema_out}")


# ---------------------------------------------------------------------------- #
# 2. generate                                                                  #
# ---------------------------------------------------------------------------- #
@cli.command("generate")
@click.argument(
    "schema_json", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "-n",
    "--rows",
    type=int,
    required=True,
    help="Number of synthetic rows to create",
)
@click.option(
    "-o",
    "--out",
    "out_csv",
    required=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Where to write the generated CSV",
)
def generate_cmd(schema_json: Path, rows: int, out_csv: Path) -> None:
    """Generate synthetic rows from SCHEMA_JSON into --out CSV file."""
    schema = load_schema(schema_json)
    validate_schema(schema)
    df = generate_rows(schema, rows)
    save_rows(df, out_csv)
    click.echo(f"✅  Generated {rows:,} rows → {out_csv}")


# ---------------------------------------------------------------------------- #
# 3. validate                                                                  #
# ---------------------------------------------------------------------------- #
@cli.command("validate")
@click.argument("schema_json", type=click.Path(exists=True, dir_okay=False))
def validate_cmd(schema_json: str) -> None:
    """Check SCHEMA_JSON is structurally sound."""
    try:
        validate_schema(load_schema(schema_json))
        click.echo("✅  Schema is valid")
    except ValueError as err:
        click.echo(f"❌  {err}", err=True)
        raise SystemExit(1)


# ---------------------------------------------------------------------------- #
# 4. preview (convenience)                                                     #
# ---------------------------------------------------------------------------- #
@cli.command("preview")
@click.argument(
    "schema_json", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("-n", "--rows", default=5, show_default=True, help="Rows to preview")
def preview_cmd(schema_json: Path, rows: int) -> None:
    """Print a small synthetic sample (no file written)."""
    schema = load_schema(schema_json)
    df = generate_rows(schema, rows)
    # Use pandas' pretty printing
    with pd.option_context("display.max_columns", None):
        click.echo(df.head(rows).to_markdown(index=False))


# ---------------------------------------------------------------------------- #
# Aliases for backwards compatibility                                          #
# ---------------------------------------------------------------------------- #
cli.add_command(profile_cmd, name="prof")  # datadepth prof …
cli.add_command(generate_cmd, name="gen")  # datadepth gen  …
# ────────────────────────────────────────────────────────────────────────────
