from pathlib import Path
import plotly.io as pio

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


def write_fig(fig, output: Path):
    """
    Writes a plotly figure to file.

    Args:
        fig (plotly figure): The figure to be written
        output (Path): The path to the output file.
            If the directory does not exist, then it is created.
            Output can be PDF, SVG, JPG, PNG or HTML based on the extension.
    """
    output.parent.mkdir(exist_ok=True, parents=True)
    if output.suffix.lower() == ".html":
        fig.write_html(output)
    else:
        fig.write_image(output)
