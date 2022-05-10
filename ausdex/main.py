from pathlib import Path
from typing import List, Union
import webbrowser
import typer

import importlib_metadata as lib_metadata
from typing import Optional
import subprocess

from ausdex import calc_inflation

app = typer.Typer()


def version_callback(value: bool):
    if value:
        version = lib_metadata.version("ausdex")
        typer.echo(version)
        raise typer.Exit()


@app.command()
def repo():
    """
    Opens the repository in a web browser.
    """
    typer.launch("https://github.com/rbturnbull/ausdex")


@app.command()
def docs(live: bool = True):
    """Builds the documentation.

    Args:
        live (bool, optional): Whether or not to use sphinx-autobuild to automatically build the documentation as files are edited. Defaults to True.
    """
    root_dir = Path(__file__).parent.parent.resolve()
    docs_dir = root_dir / "docs"
    docs_build_dir = docs_dir / "_build/html"

    if live:
        command = f"sphinx-autobuild {docs_dir} {docs_build_dir} --open-browser"
    else:
        command = f"sphinx-build -E -b html {docs_dir} {docs_build_dir}"

    subprocess.run(command, shell=True)

    if not live:
        index_page = docs_build_dir / "index.html"
        print(f"Open the index page at {index_page}")
        webbrowser.open_new("file://" + str(index_page))


@app.command()
def inflation(
    value: float,
    original_date: str,
    evaluation_date: str = None,
):
    """Adjusts Australian dollars for inflation.

    Prints output to stdout.

    Args:
        value (float): The dollar value to be converted.
        original_date (str): The date that the value is in relation to.
        evaluation_date (str, optional): The date to adjust the value to. Defaults to the current date.
    """

    result = calc_inflation(value=value, original_date=original_date, evaluation_date=evaluation_date)
    typer.echo(f"{result:.2f}")


@app.command()
def plot_inflation(
    compare_date: str,
    out: Path,
    start_date: str = typer.Option(None),
    end_date: str = typer.Option(None),
    value: float = typer.Option(1.0),
):
    """function to plot a time series of dollar values attached to a particular date's dollar value.

    saves output to html file

    Args:
        compare_date (str): Date to set relative value of the dollars too.
        out (Path): Path to html file where plot will be saved.
        start_date (Union[datetime, str, None], optional): Date to set the beginning of the time series graph. Defaults to None, which starts in 1948.
        end_date (Union[datetime, str, None], optional): Date to set the end of the time series graph too. Defaults to None, which will set the end date to the most recent quarter.
        value (Union[float, int], optional): Value you in `compare_date` dollars to plot on the time series. Defaults to 1.


    """
    from ausdex.inflation import plot_inflation_timeseries

    fig = plot_inflation_timeseries(compare_date=compare_date, start_date=start_date, end_date=end_date, value=value)
    fig.write_html(out)


@app.command()
def plot_cpi(
    out: Path,
    start_date: str = typer.Option(None),
    end_date: str = typer.Option(None),
):
    """function to plot the Australian CPI vs time

    Saves plot as html in out

    Args:
        out (Path): Path to html file where plot will be saved.
        start_date (Union[datetime, str, None], optional): Date to set the beginning of the time series graph. Defaults to None, which starts in 1948.
        end_date (Union[datetime, str, None], optional): Date to set the end of the time series graph too. Defaults to None, which will set the end date to the most recent quarter.

    """
    from ausdex.inflation import plot_cpi_timeseries

    fig = plot_cpi_timeseries(start_date=start_date, end_date=end_date)
    fig.write_html(out)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True),
):
    """Adjusts Australian dollars for inflation."""
    pass
