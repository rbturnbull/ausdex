import typer
from pathlib import Path
from typing import List
from datetime import datetime
import importlib.metadata
from typing import Optional
import subprocess

from aucpi import adjust as call_adjust

app = typer.Typer()


def version_callback(value: bool):
    if value:
        version = importlib.metadata.version("aucpi")
        typer.echo(version)
        raise typer.Exit()


@app.command()
def repo():
    """
    Opens the repository in a web browser
    """
    typer.launch("https://github.com/rbturnbull/aucpi")


@app.command()
def docs():
    """
    Builds the documentation.
    """
    root_dir = Path(__file__).parent.parent.resolve()
    docs_dir = root_dir / "docs"
    docs_build_dir = docs_dir / "_build/html"

    subprocess.run(
        f"sphinx-autobuild {docs_dir} {docs_build_dir} --open-browser", shell=True
    )


@app.command()
def adjust(
    value: float,
    original_date: str,
    evaluation_date: str = None,
):
    """Adjusts Australian dollars for inflation"""
    result = call_adjust(
        value=value, original_date=original_date, evaluation_date=evaluation_date
    )
    typer.echo(f"{result:.2f}")


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    ),
):
    """Adjusts Australian dollars for inflation"""
    pass
