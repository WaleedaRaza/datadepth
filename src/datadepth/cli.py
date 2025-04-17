# src/datadepth/cli.py

import click
from datadepth.profiler import profile_data
from datadepth.generator import generate_data

@click.group()
def cli():
    pass

@cli.command()
@click.argument("file", type=click.Path(exists=True))
def profile(file):
    profile_data(file)

@cli.command()
@click.argument("schema_path", type=click.Path(exists=True))
@click.option("--rows", default=100, help="Number of rows to generate")
@click.option("--out", default="synthetic.csv", help="Output CSV path")
def generate(schema_path, rows, out):
    generate_data(schema_path, rows, out)

if __name__ == "__main__":
    cli()
