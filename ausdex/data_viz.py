import plotly.express as px
import plotly
import geopandas as gpd
import pandas as pd
from typing import Union


def create_choropleth_from_geodf(
    geo_df: gpd.GeoDataFrame, color_column: str, simplify: float = 0, **kwargs
) -> plotly.graph_objects.Figure:
    """this function creates plotly choropleth maps from geopandas geodataframes using the column specified in color_column.

    This function has a simplify argument to use the gpd.GeoSeries.simplify method to simplify the features and improve performance.

    Args:
        geo_df (gpd.GeoDataFrame): polygon geodataframe to plot on the choropleth map
        color_column (str): name of the column in gdf to set the colors in the choropleth.
        simplify (float, optional): map scale value to simplify polygons too according to gpd.GeoSeries.simplify method. Defaults to 0.
        kwargs (dict, option): optional additional parameters to feed into plotly.express.choropleth function.

    Returns:
        plotly.graph_objects.Figure: plotly choropleth object.
    """
    if simplify > 0:
        geo_df.geometry = geo_df.geometry.simplify(simplify)
    fig = px.choropleth(
        geo_df,
        geojson=geo_df.geometry,
        locations=geo_df.index,
        color=color_column,
        projection="mercator",
        fitbounds="locations",
        basemap_visible=False,
        **kwargs
    )
    return fig


def create_line_plot(
    df: Union[pd.DataFrame, gpd.GeoDataFrame],
    x_col: str,
    y_col: str,
    color_col: str,
    **kwargs
):
    return px.line(df, x=x_col, y=y_col, color=color_col, **kwargs)
