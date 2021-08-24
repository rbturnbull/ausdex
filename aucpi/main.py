import typer
from pathlib import Path
from typing import List
from datetime import datetime
import importlib.metadata
from typing import Optional

from aucpi import adjust

app = typer.Typer()

def version_callback(value: bool):
    if value:
        version = importlib.metadata.version("aucpi")
        typer.echo(version)
        raise typer.Exit()

@app.command()
def main(
    value: float,
    original_date: str,
    evaluation_date: str = None,
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    ),
):
    """ Adjusts Australian dollars for inflation """
    result = adjust(value=value, original_date=original_date, evaluation_date=evaluation_date)
    typer.echo(f"{result:.2f}")
