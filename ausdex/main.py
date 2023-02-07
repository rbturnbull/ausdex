from pathlib import Path
from typing import List, Union
import webbrowser
import typer


from typing import Optional
import subprocess

from .inflation import calc_inflation
from .location import Location
from . import viz

app = typer.Typer()


def version_callback(value: bool):
    if value:
        import importlib_metadata as lib_metadata
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
    value: float = typer.Argument(..., help="The dollar value to be converted."),
    original_date: str = typer.Argument(..., help="The date that the value is in relation to."),
    evaluation_date: str = typer.Option(None, help="The date to adjust the value to. Defaults to the current date."),
    location: Location = typer.Option(
        Location.AUSTRALIA, case_sensitive=False, help="The location for calculating the CPI."
    ),
):
    """
    Adjusts Australian dollars for inflation.

    Prints output to stdout.

    Args:
        value (float): The dollar value to be converted.
        original_date (str): The date that the value is in relation to.
        evaluation_date (str, optional): The date to adjust the value to. Defaults to the current date.
        location (Location, optional): The location for calculating the CPI.
            Options are 'Australia', 'Sydney', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin', and 'Canberra'.
            Default is 'Australia'.
    """

    result = calc_inflation(
        value=value, original_date=original_date, evaluation_date=evaluation_date, location=location
    )
    typer.echo(f"{result:.2f}")


@app.command()
def plot_inflation(
    compare_date: str = typer.Argument(..., help="Date to set relative value of the dollars too."),
    show: bool = typer.Option(True, help="Whether or not to show the figure in a browser."),
    output: Path = typer.Option(
        None,
        help="The path to where the figure will be saved. Output can be PDF, JPG, PNG or HTML based on the extension.",
    ),
    start_date: str = typer.Option(
        None, help="Date to set the beginning of the time series graph. Defaults to None, which starts in 1948."
    ),
    end_date: str = typer.Option(
        None,
        help="Date to set the end of the time series graph too. If empty, then the end date to the most recent quarter.",
    ),
    value: float = typer.Option(
        1.0, help="Value you in `compare_date` dollars to plot on the time series. Defaults to 1."
    ),
    location: Location = typer.Option(
        Location.AUSTRALIA,
        help="The location for calculating the CPI.",
        case_sensitive=False,
    ),
):
    """
    Plots a time series of dollar values attached to a particular date's dollar value.

    Args:
        compare_date (str): Date to set relative value of the dollars too.
        out (Path): The path to where the figure will be saved. Output can be PDF, JPG, PNG or HTML based on the extension.
        start_date (str, optional): Date to set the beginning of the time series graph. Defaults to None, which starts in 1948.
        end_date (str, optional): Date to set the end of the time series graph too. Defaults to None, which will set the end date to the most recent quarter.
        value (float, optional): Value you in `compare_date` dollars to plot on the time series. Defaults to 1.
    """
    from ausdex.viz import plot_inflation_timeseries

    fig = plot_inflation_timeseries(
        compare_date=compare_date, start_date=start_date, end_date=end_date, value=value, location=location
    )
    if output:
        print(f"Writing figure to '{output}'.")
        viz.write_fig(fig, output)
    if show:
        fig.show()


@app.command()
def plot_cpi(
    show: bool = typer.Option(True, help="Whether or not to show the figure in a browser."),
    output: Path = typer.Option(
        None,
        help="The path to where the figure will be saved. Output can be PDF, JPG, PNG or HTML based on the extension.",
    ),
    start_date: str = typer.Option(
        None, help="Date to set the beginning of the time series graph. Defaults to None, which starts in 1948."
    ),
    end_date: str = typer.Option(
        None,
        help="Date to set the end of the time series graph too. If empty, then the end date to the most recent quarter.",
    ),
    location: List[Location] = typer.Option(
        None,
        help="The location for calculating the CPI.",
        case_sensitive=False,
    ),
    title: str = typer.Option(None, help="A custom title of the plot."),
):
    """
    Plot the Australian CPI over time.

    Args:
        show (bool): Whether or not to show the figure in a browser. Default True.
        output (Path): The path to where the figure will be saved. Output can be PDF, SVG, JPG, PNG or HTML based on the extension.
        start_date (str, optional): Date to set the beginning of the time series graph. If empty, it defaults to 1948.
        end_date (str, optional): Date to set the end of the time series graph too. If empty, then the end date to the most recent quarter.
        location (List[location]): The location for calculating the CPI.
        title (str, optional): A custom title of the plot.
    """
    from ausdex.viz import plot_cpi_timeseries

    fig = plot_cpi_timeseries(start_date=start_date, end_date=end_date, locations=location, title=title)
    if output:
        print(f"Writing figure to '{output}'.")
        viz.write_fig(fig, output)
    if show:
        fig.show()


@app.command()
def plot_cpi_change(
    show: bool = typer.Option(True, help="Whether or not to show the figure in a browser."),
    start_date: str = typer.Option(
        None, help="Date to set the beginning of the time series graph. Defaults to None, which starts in 1948."
    ),
    end_date: str = typer.Option(
        None,
        help="Date to set the end of the time series graph too. If empty, then the end date to the most recent quarter.",
    ),
    output: Path = typer.Option(
        None,
        help="The path to where the figure will be saved. Output can be PDF, JPG, PNG or HTML based on the extension.",
    ),
    location: List[Location] = typer.Option(
        None,
        help="The location for calculating the CPI.",
        case_sensitive=False,
    ),
    title: str = typer.Option(None, help="A custom title of the plot."),
):
    """
    Produces a plot of the percentage change from corresponding quarter of previous year.

    Args:
        show (bool): Whether or not to show the figure in a browser. Default True.
        output (Path): The path to where the figure will be saved. Output can be PDF, SVG, JPG, PNG or HTML based on the extension.
        location (List[location]): The location for calculating the CPI.
    """
    from ausdex.viz import plot_cpi_change

    fig = plot_cpi_change(
        start_date=start_date,
        end_date=end_date,
        output=output,
        locations=location,
        title=title,
    )
    if show:
        fig.show()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True),
):
    """Adjusts Australian dollars for inflation."""
    pass
