from pathlib import Path
from datetime import datetime
from datetime import timedelta
from typing import Union, List

import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px

from .location import Location
from .inflation import latest_cpi_df, CPI
from .dates import convert_date


pio.kaleido.scope.mathjax = None


def format_fig(fig):
    """Formats a plotly figure in a nicer way."""
    fig.update_layout(
        width=1200,
        height=550,
        plot_bgcolor="white",
        title_font_color="black",
        font=dict(
            family="Linux Libertine Display O",
            size=18,
            color="black",
        ),
    )
    gridcolor = "#dddddd"
    fig.update_xaxes(gridcolor=gridcolor)
    fig.update_yaxes(gridcolor=gridcolor)

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True, ticks='outside')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True, ticks='outside')


def write_fig(fig, output: Union[Path, str]):
    """
    Writes a plotly figure to file.

    Args:
        fig (plotly figure): The figure to be written
        output (Path): The path to the output file.
            If the directory does not exist, then it is created.
            Output can be PDF, SVG, JPG, PNG or HTML based on the extension.
    """
    if not output:
        return

    output = Path(output)
    output.parent.mkdir(exist_ok=True, parents=True)
    if output.suffix.lower() == ".html":
        fig.write_html(output)
    else:
        fig.write_image(output)


def plot_inflation_timeseries(
    compare_date: Union[datetime, str],
    start_date: Union[datetime, str, None] = None,
    end_date: Union[datetime, str, None] = None,
    value: Union[float, int] = 1,
    location: Union[Location, str] = Location.AUSTRALIA,
    **kwargs,
) -> go.Figure:
    """
    Plots a time series of dollar values attached to a particular date's dollar value

    Args:
        compare_date (datetime, str): Date to set relative value of the dollars too.
        start_date (datetime, str, optional): Date to set the beginning of the time series graph. Defaults to None, which starts in 1948.
        end_date (datetime, str, optional): Date to set the end of the time series graph too. Defaults to None, which will set the end date to the most recent quarter.
        value (float, int, optional): Value you in `compare_date` dollars to plot on the time series. Defaults to 1.
        location (Location, str, optional): The location for calculating the CPI.
            Options are 'Australia', 'Sydney', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin', and 'Canberra'.
            Default is 'Australia'.
        kwargs: (Optional(dict)): additional parameters to feed into plotly.express.line function

    Returns:
        plotly.graph_objects.Figure: line graph of inflated dollar values vs time
    """
    cpi = CPI()

    inflation = cpi.calc_inflation_timeseries(
        compare_date, start_date, end_date, value=value, location=location
    ).reset_index()
    new_col_name = f"Equivalent Dollar Value"
    if "title" not in kwargs:
        kwargs["title"] = f"The equivalent of ${value:.2f} from {str(compare_date)}"
    inflation.rename(
        columns={cpi.column_name(location): new_col_name},
        inplace=True,
    )
    fig = px.line(inflation, x="Date", y=new_col_name, **kwargs)
    format_fig(fig)
    return fig


def plot_cpi_timeseries(
    start_date: Union[datetime, str, None] = None,
    end_date: Union[datetime, str, None] = None,
    locations: List[Location] = None,
    title: str = None,
    **kwargs,
) -> go.Figure:
    """
    Plots CPI vs time.

    Args:
        start_date (datetime, str, optional): Date to set the beginning of the time series graph. Defaults to None, which starts in 1948.
        end_date (datetime, str, optional): Date to set the end of the time series graph too. Defaults to None, which will set the end date to the most recent quarter.
        locations (List[Location], optional): The location(s) for calculating the CPI.
            Options are 'Australia', 'Sydney', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin', and 'Canberra'.
            Default is 'Australia'.
        title: (str, optional): The title of the figure.
        kwargs:: additional parameters to feed into plotly.express.line function.

    Returns:
        plotly.graph_objects.Figure: plot of cpi vs time
    """
    if not locations:
        locations = list(Location)

    if start_date is not None:
        start_date = convert_date(start_date).item()
    if end_date is not None:
        end_date = convert_date(end_date).item()

    df = latest_cpi_df()
    cpi = CPI()
    column_map = {cpi.column_name(location): str(location) for location in locations}
    df = df.rename(columns=column_map)
    df = df[column_map.values()]
    df = df[start_date:end_date].copy()
    df = df.reset_index()

    fig = px.line(df, x="Date", y=list(column_map.values()), **kwargs)
    fig.update_layout(
        yaxis_title="CPI",
        legend_title="Location",
    )

    if title is None:
        location_name = locations[0] if len(locations) == 1 else "Australia"
        title = f"Consumer Price Index in {location_name} over time"

    fig.update_layout(title=title)

    if len(locations) == 1:
        fig.update_layout(
            showlegend=False,
        )
    format_fig(fig)
    return fig


def plot_cpi_change(
    start_date: Union[datetime, str, None] = None,
    end_date: Union[datetime, str, None] = None,
    output: Union[Path, str, None] = None,
    locations: List[Location] = None,
    title: str = None,
    rba_target: bool = True,
) -> go.Figure:
    """
    Produces a plot of the percentage change from corresponding quarter of previous year.

    Args:
        start_date (datetime, str, optional): Date to set the beginning of the time series graph. Defaults to None, which starts in 1948.
        end_date (datetime, str, optional): Date to set the end of the time series graph too. Defaults to None, which will set the end date to the most recent quarter.
        output (Path, str, None): If given, then the plot is written to this path.

    Returns:
        go.Figure: The resulting plotly figure.
    """
    if not locations:
        locations = list(Location)

    df = latest_cpi_df()
    df = df[start_date:end_date].copy()

    if start_date is not None:
        start_date = convert_date(start_date).item()
    if end_date is not None:
        end_date = convert_date(end_date).item()

    fig = go.Figure()
    for location in locations:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[f'Percentage Change from Corresponding Quarter of Previous Year ;  All groups CPI ;  {location} ;']
                / 100,
                name=str(location) if len(locations) > 1 else "CPI Change",
                line=dict(width=4.0 if location == Location.AUSTRALIA else 1.5),
                visible=1 if location == Location.AUSTRALIA else "legendonly",
            )
        )
    if rba_target:
        start_target = datetime(1992, 8, 17)
        fig.add_trace(
            go.Scatter(
                x=[start_target, df.index.max(), df.index.max(), start_target],
                y=[0.02, 0.02, 0.03, 0.03],
                fill='toself',
                fillcolor='rgba(0,176,246,0.2)',
                line_color='rgba(255,255,255,0)',
                name='RBA Target',
                showlegend=True,
            )
        )

    if title is None:
        location_name = locations[0] if len(locations) == 1 else "Australia"
        title = f"Percentage change from corresponding quarter of previous year in {location_name}"

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Percentage Change",
        yaxis_tickformat=',.0%',
        xaxis_range=(df.index.min(), df.index.max() + timedelta(days=200)),
    )
    fig.update_yaxes(zeroline=True, zerolinewidth=1, zerolinecolor='Black')

    format_fig(fig)
    write_fig(fig, output)

    return fig
