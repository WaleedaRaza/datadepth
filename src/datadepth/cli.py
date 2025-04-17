import click
from .profiler import profile_csv, save_schema

@click.group()            # <‑‑ this decorator must wrap a function **named cli**
def cli():
    """DataDepth CLI root."""
    pass


@cli.command(help="Profile a CSV and write schema JSON")
@click.argument("csv_path", type=click.Path(exists=True))
@click.option("-o", "--out", default="schema.json", show_default=True)
def profile(csv_path, out):
    schema = profile_csv(csv_path)
    save_schema(schema, out)
    click.echo(f"Schema saved → {out}")

@cli.command(help="Generate synthetic rows from a schema JSON.")
@click.argument("schema_json", type=click.Path(exists=True))
@click.option("-n", "--rows", default=1000, show_default=True)
@click.option("-o", "--out", default="synthetic.csv", show_default=True)
def generate(schema_json, rows, out):
    from .generator import generate_from_schema, save_df
    df = generate_from_schema(schema_json, rows)
    save_df(df, out)
    click.echo(f"Generated {rows:,} rows → {out}")
