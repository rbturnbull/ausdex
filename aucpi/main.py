import typer
from pathlib import Path
from typing import List
from datetime import datetime
import webbrowser

import sys

if sys.version_info.minor <= 7:
    import importlib_metadata as lib_metadata
else:
    import importlib.metadata as lib_metadata
from typing import Optional
import subprocess

from aucpi.seifa_vic.seifa_vic import Metric
from aucpi import adjust as call_adjust

app = typer.Typer()


def version_callback(value: bool):
    if value:
        version = lib_metadata.version("aucpi")
        typer.echo(version)
        raise typer.Exit()


@app.command()
def repo():
    """
    Opens the repository in a web browser
    """
    typer.launch("https://github.com/rbturnbull/aucpi")


@app.command()
def docs(live: bool = True):
    """
    Builds the documentation.
    """
    root_dir = Path(__file__).parent.parent.resolve()
    docs_dir = root_dir / "docs"
    docs_build_dir = docs_dir / "_build/html"

    if live:
        command = f"sphinx-autobuild {docs_dir} {docs_build_dir} --open-browser"
    else:
        command = f"sphinx-build -b html {docs_dir} {docs_build_dir}"

    subprocess.run(command, shell=True)

    if not live:
        index_page = docs_build_dir / "index.html"
        print(f"Open the index page at {index_page}")
        webbrowser.open_new("file://" + str(index_page))


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


@app.command()
def seifa_vic(
    year_value: float, suburb: str, metric: Metric, fill_value: str = "extrapolate"
):
    """
    interpolates suburb aggregated socioeconomic indices for a given year for a given suburb

    inputs
    year_value (int, float): The year or array of year values you want interpolated\n
        suburb (str): The name of the suburb that you want the data interpolated for\n
                metric (str): the name of the seifa_score variable, options are include\n
                `irsd_score` for index of relative socio economic disadvantage,\n
                `ieo_score` for the index of education and opportunity,\n
                `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,\n
                `uirsa_score` for the urban index of relative socio economic advantage,\n
                `rirsa_score` for the rural index of relative socio economic advantage\n
                fill_value (str): can be "extrapolate" to extraplate past the extent of the dataset or "boundary_value" to use the closest datapoint, or \n
                or an excepted response for scipy.interpolate.interp1D fill_value keyword argument\n
    outputs
        interpolated score (float)

    """
    import warnings

    warnings.filterwarnings("ignore")

    from .seifa_vic import interpolate_vic_suburb_seifa

    result = interpolate_vic_suburb_seifa(
        year_value, suburb.upper(), metric.value, fill_value=fill_value
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
