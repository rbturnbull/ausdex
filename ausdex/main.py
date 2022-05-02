from pathlib import Path
from typing import List, Union
import webbrowser
import typer

import importlib_metadata as lib_metadata
from typing import Optional
import subprocess

from ausdex.seifa_vic.seifa_vic import Metric
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


@app.command()
def seifa_vic(
    year_value: str,
    suburb: str,
    metric: Metric,
    lga: Union[str, None] = None,
    fill_value: str = "null",
    guess_misspelt: bool = False,
):
    """
    Interpolates suburb aggregated socio-economic indexes for a given year for a given suburb.

    Args:
        year_value (int, float, str): Year values in decimal years or in a string datetime format convertable by pandas.to_datetime function\n
        suburb (str): The name of the suburb that you want the data interpolated for\n
                metric (str): the name of the seifa_score variable, options are include\n
                `irsd_score` for index of relative socio-economic disadvantage,\n
                `ieo_score` for the index of education and opportunity,\n
                `ier_score` for an index of economic resources, `irsad_score` for index of socio-economic advantage and disadvantage,\n
                `uirsa_score` for the urban index of relative socio-economic advantage,\n
                `rirsa_score` for the rural index of relative socio-economic advantage\n
        lga (str None): local government area. Only necessary for suburb names that are repeated in the state\n
        fill_value (str): can be "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or \n
                or an excepted response for scipy.interpolate.interp1D fill_value keyword argument\n
        guess_misspelt (bool): If true, then if it cannot find a match for the name of the suburb then it finds the closest name to it.
    Returns:
        interpolated score (float)

    """
    import warnings

    warnings.filterwarnings("ignore")

    from .seifa_vic import interpolate_vic_suburb_seifa

    result = interpolate_vic_suburb_seifa(
        year_value,
        suburb.upper(),
        metric.value,
        lga=lga,
        fill_value=fill_value,
        guess_misspelt=guess_misspelt,
    )
    typer.echo(f"{result:.2f}")


@app.command()
def seifa_vic_gis(
    date: str,
    metric: Metric,
    out: Path,
    fill_value: str = "null",
):
    """Interpolates aggregated socio-economic indexes for a given date for all suburbs and saves them to a GIS file.

    Args:
        date (int, float, str): Year values in decimal years or in a string datetime format convertable by pandas.to_datetime function\n
        metric (str): the name of the seifa_score variable, options are include\n
                `irsd_score` for index of relative socio-economic disadvantage,\n
                `ieo_score` for the index of education and opportunity,\n
                `ier_score` for an index of economic resources,\n
                `irsad_score` for index of socio-economic advantage and disadvantage,\n
                `uirsa_score` for the urban index of relative socio-economic advantage,\n
                `rirsa_score` for the rural index of relative socio-economic advantage\n
        out (Path): Path to save html graph to.\n
        fill_value (str): can be "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or \n
                or an excepted response for scipy.interpolate.interp1D fill_value keyword argument\n

    Returns:
        interpolated score (float)

    """
    import warnings

    warnings.filterwarnings("ignore")

    from .seifa_vic import get_seifa_gis

    suburbs_df = get_seifa_gis(
        date,
        metric.value,
        fill_value=fill_value,
    )

    # Write file
    directory = out.parent
    directory.mkdir(exist_ok=True, parents=True)
    suburbs_df.to_file(out)


@app.command()
def seifa_vic_map(
    date: str,
    metric: Metric,
    out: Path,
    fill_value: str = "null",
    min_x: float = typer.Option(None),
    min_y: float = typer.Option(None),
    max_x: float = typer.Option(None),
    max_y: float = typer.Option(None),
    clip_mask: Path = typer.Option(None),
):
    """Interpolates aggregated socio-economic indexes for a given date for all suburbs and saves them to a a plotly map html file.

    Args:

        date (int, float, str): Year values in decimal years or in a string datetime format convertable by pandas.to_datetime function\n
        metric (str): the name of the seifa_score variable, options are include\n
                `irsd_score` for index of relative socio-economic disadvantage,\n
                `ieo_score` for the index of education and opportunity,\n
                `ier_score` for an index of economic resources,\n
                `irsad_score` for index of socio-economic advantage and disadvantage,\n
                `uirsa_score` for the urban index of relative socio-economic advantage,\n
                `rirsa_score` for the rural index of relative socio-economic advantage\n
        out (Path): Path to save html graph to.\n
        fill_value (str): can be "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or \n
                or an excepted response for scipy.interpolate.interp1D fill_value keyword argument\n
        min_x (Union[None,float], optional):  minimum x coordinate boundary of intersecting polygons to plot. Defaults to None.\n
        min_y (Union[None,float], optional): maximum x coordinate boundary of intersecting polygons to plot. Defaults to None.\n
        max_x (Union[None,float], optional): minimum y coordinate boundary of intersecting polygons to plot Defaults to None.\n
        max_y (Union[None,float], optional): maximum y coordinate boundary of intersecting polygons to plot. Defaults to None.\n
        clip_mask (Path, optional): path to mask polygon data to clip the dataset to, overrides min_x, max_x, min_y, max_y. Defaults to None.


    Returns:
        None

    """
    import warnings

    warnings.filterwarnings("ignore")

    from .seifa_vic import get_seifa_map

    if type(clip_mask) == Path:
        import geopandas as gpd

        clip_mask = gpd.read_file(clip_mask)

    out_fig = get_seifa_map(
        date,
        metric.value,
        fill_value=fill_value,
        min_x=min_x,
        min_y=min_y,
        max_x=max_x,
        max_y=max_y,
        clip_mask=clip_mask,
    )

    # Write file
    directory = out.parent
    directory.mkdir(exist_ok=True, parents=True)

    out_fig.write_html(out)


@app.command()
def seifa_vic_plot(metric: Metric, out: Path, suburbs: List[str]):
    """Creates a time series of seifa metrics for a given suburb or set of suburbs as a plotly line graph and saves the html file.

    Args:
        metric (Union[Metric, str]): metric to plot along the time series.\n
        out (Path): Path to html file where plot will be saved
        suburbs (Union[list, np.array, pd.Series, str]): list of suburbs to include in the time series
    """
    from .seifa_vic import create_timeseries_chart

    out_fig = create_timeseries_chart(suburbs=suburbs, metric=metric)
    # Write file
    directory = out.parent
    directory.mkdir(exist_ok=True, parents=True)

    out_fig.write_html(out)


@app.command()
def seifa_vic_assemble():
    """This function re-assembles the victorian dataset from Aurin and Seifa data"""
    from .seifa_vic import SeifaVic

    seifa_vic = SeifaVic(True)
    seifa_vic._load_data()
    typer.echo("Data loaded")


@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True),
):
    """Adjusts Australian dollars for inflation or returns interpolated socio-economic indexes for Victorian suburbs."""
    pass
