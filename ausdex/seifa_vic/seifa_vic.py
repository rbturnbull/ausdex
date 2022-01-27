import enum
import datetime
from difflib import get_close_matches
from typing import Union
import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import modin.pandas as mpd
import plotly
import warnings

from ..data_viz import create_choropleth_from_geodf, create_line_plot
from ..gis_utils import clip_gdf
from ..dates import date_time_to_decimal_year
from .data_wrangling import preprocess_victorian_datasets, wrangle_victorian_gis_data


DOUBLE_NAMES = [
    "ASCOT - BALLARAT",
    "ASCOT - GREATER BENDIGO",
    "BELLFIELD - BANYULE",
    "BELLFIELD - GRAMPIANS",
    "BIG HILL - GREATER BENDIGO",
    "BIG HILL - SURF COAST",
    "FAIRY DELL - CAMPASPE",
    "FAIRY DELL - EAST GIPPSLAND",
    "FRAMLINGHAM - MOYNE",
    "GOLDEN POINT - BALLARAT",
    "GOLDEN POINT - CENTRAL GOLDFIELDS",
    "GOLDEN POINT - MOUNT ALEXANDER",
    "HAPPY VALLEY - GOLDEN PLAINS",
    "HAPPY VALLEY - SWAN HILL",
    "HILLSIDE - EAST GIPPSLAND",
    "HILLSIDE - MELTON",
    "KILLARA - GLENELG",
    "KILLARA - WODONGA",
    "MERRIJIG - EAST GIPPSLAND",
    "MERRIJIG - MANSFIELD",
    "MERRIJIG - WANGARATTA",
    "MOONLIGHT FLAT - CENTRAL GOLDFIELDS",
    "MOONLIGHT FLAT - MOUNT ALEXANDER",
    "MYALL - BULOKE",
    "MYALL - GANNAWARRA",
    "NEWTOWN - GOLDEN PLAINS",
    "NEWTOWN - GREATER GEELONG",
    "REEDY CREEK - MITCHELL",
    "SPRINGFIELD - MACEDON RANGES",
    "SPRINGFIELD - SWAN HILL",
    "STONY CREEK - HEPBURN",
    "STONY CREEK - SOUTH GIPPSLAND",
    "THOMSON - BAW BAW",
    "THOMSON - GREATER GEELONG",
]


metrics = [
    "ier_score",
    "irsd_score",
    "ieo_score",
    "irsad_score",
    "rirsa_score",
    "uirsa_score",
]
Metric = enum.Enum("Metric", {metric: metric for metric in metrics})


def _make_nan(x):

    if type(x) != np.array:
        x = np.array(x)
    return x * np.nan


def _make_cache_key(suburb, metric, fill_value, **kwargs):
    test_kwargs = {"test1": "test2"}
    key_val_list = [
        f"{str(key)}_{str(kwargs[key])}" for key in sorted(list(kwargs.keys()))
    ]
    return f"{suburb}_{metric}_{fill_value}_" + "_".join(key_val_list)


class SeifaVic:
    """This object loads, or creates the combined dataset for the SEIFA_VIC interpolations"""

    def __init__(self, force_rebuild=False):
        """initialising SeifaVic object

        Args:
            force_rebuild (bool, optional): forces the reconstruction of the combined dataset if already built and saved in user data. Defaults to False.
        """
        self.metrics = [
            "ier_score",
            "irsd_score",
            "ieo_score",
            "irsad_score",
            "rirsa_score",
            "uirsa_score",
        ]
        self.double_names = DOUBLE_NAMES
        self.force_rebuild = force_rebuild
        self.interp_cache = {}

    def _load_data(self):
        """loads the preprocessed victorian dataset if it hasn't been loaded already"""
        if "df" not in self.__dict__:
            # print('loading data')
            self.df = preprocess_victorian_datasets(force_rebuild=self.force_rebuild)
            for col in ["year"] + self.metrics:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

    def _load_gis(self):
        if "suburbs" not in self.__dict__:
            suburbs, _ = wrangle_victorian_gis_data()
            self.suburbs = suburbs

    def _fix_double_suburbs(self, suburb: str, lga: str) -> str:
        comb = f"{suburb} - {lga}"
        if comb in self.double_names:
            return comb
        else:
            return suburb

    def get_suburb_data(self, suburb: str):
        """returns the dataset (self.df) filtered to a suburb

        Args:
            suburb (str): suburb that dataset will be filtered too(must be all caps)

        Returns:
            pd.DataFrame: filtered dataframe with only the data from that suburb
        """
        return self.df[self.df["Site_suburb"] == suburb]

    def build_interpolator(
        self,
        suburb: str,
        metric: str,
        fill_value: Union[str, np.array, tuple],
        guess_misspelt: bool = False,
        **kwargs,
    ) -> interp1d:
        """this function builds an interpolator with the "year" column as the x, and the metric column as the y

        Args:
            suburb (str): suburb that dataset will be filtered too(must be all caps)
            metric (str): 'ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score', the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.

            fill_value (Union[str, np.array, tuple]): Specifies the values returned outside the range of the ABS census datasets. It can be "null" to return np.nan values, "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument.
            guess_misspelt (bool): Tries to guess the suburb if the particular spelling is not found in the dataset. Otherwise it returns a NaN.

        Returns:
            scipy.interpolate.interp1d: interpolator object for the suburb and metric
        """
        df = self.get_suburb_data(suburb).dropna(subset=[metric]).sort_values("year")

        if len(df) == 0:
            close_matches = get_close_matches(suburb, self.df["Site_suburb"].unique())
            if guess_misspelt and close_matches:
                warnings.warn(f"No suburb named '{suburb}'. Using '{close_matches[0]}'")
                df = (
                    self.get_suburb_data(close_matches[0])
                    .dropna(subset=[metric])
                    .sort_values("year")
                )
            else:
                message = f"No suburb named '{suburb}'. Returning NaN."
                if close_matches:
                    message += f" Did you mean one of {close_matches}?"
                warnings.warn(message)
                return _make_nan

        if fill_value == "boundary_value":
            if len(df[metric]) == 0:
                fill_value = (np.nan, np.nan)
            else:
                fill_value = (df[metric].values[0], df[metric].values[-1])
        elif fill_value == "null":
            fill_value = (np.nan, np.nan)
        kwargs["bounds_error"] = False
        if df.shape[0] > 1:
            return interp1d(
                df["year"].values, df[metric].values, fill_value=fill_value, **kwargs
            )
        elif df.shape[0] == 1:
            if fill_value in ["extrapolate", "boundary"]:
                warnings.warn(
                    f"Suburb '{suburb}' only has one value for {metric}, assuming flat line"
                )

                def flat_interpolate(x):
                    if type(x) != np.array:
                        x = np.array(x)
                    return x * 0 + df[metric][0].item()

                return flat_interpolate

        warnings.warn(f"Cannot interpolate value for '{suburb}'.")
        return _make_nan

    def get_interpolator(
        self,
        suburb: str,
        metric: str,
        fill_value: Union[str, np.array, tuple],
        guess_misspelt: bool = False,
        **kwargs,
    ) -> interp1d:
        cache_name = _make_cache_key(suburb, metric, fill_value, **kwargs)
        if cache_name not in self.interp_cache:

            self.interp_cache[cache_name] = self.build_interpolator(
                suburb,
                metric,
                fill_value=fill_value,
                guess_misspelt=guess_misspelt,
                **kwargs,
            )
        return self.interp_cache[cache_name]

    def get_seifa_interpolation(
        self,
        year_values: Union[int, float, np.array, list],
        suburb: str,
        metric: Union[Metric, str],
        lga: Union[str, None] = None,
        fill_value: Union[str, np.array, tuple] = "null",
        _convert_data=True,
        guess_misspelt: bool = False,
        **kwargs,
    ) -> Union[float, np.array]:
        """method to get an interpolated estimate of a SEIFA score for each victorian suburb from Australian Bureau of statistics data

        Args:
            year_values (Union[int,float,np.array, list]): The year or array of year values you want interpolated.
            suburb (str): The name of the suburb that you want the data interpolated for (capitalisation doesn't matter).
            metric (Union[Metric, str]): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.
            fill_value (Union[str, np.array, tuple], optional): Specifies the values returned outside the range of the ABS census datasets. It can be "null" and return np.nan values,  "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'null'.
            _convert_data (bool): if true, will convert datetime values to decimal years, only false when batching
            **kwargs(dict-like): additional keyword arguments for scipy.interpolate.interp1D object.

        Returns:
            Union[float, np.array]: The interpolated value (s) of that seifa variable at that year(s). np.array if year_value contains multiple years.
        """
        self._load_data()
        if type(metric) == Metric:
            metric = metric.value

        if _convert_data == True:
            year_values = date_time_to_decimal_year(year_values)

        if type(lga) == str:
            suburb = self._fix_double_suburbs(
                suburb.upper().strip(), lga.upper().strip()
            )

        out = self.get_interpolator(
            suburb,
            metric,
            fill_value=fill_value,
            guess_misspelt=guess_misspelt,
            **kwargs,
        )(year_values)

        out[out < 0] = 0

        return out

    def get_seifa_interpolation_batch(
        self,
        year_values: Union[int, float, np.array, np.datetime64, list],
        suburb: Union[list, np.array, pd.Series, mpd.Series],
        metric: Union[Metric, str],
        lga: Union[list, np.array, pd.Series, mpd.Series, None] = None,
        fill_value: Union[str, np.array, tuple] = "null",
        guess_misspelt: bool = False,
        **kwargs,
    ) -> Union[float, np.array]:

        if type(metric) == Metric:
            metric = metric.value
        self._load_data()
        if type(suburb) != np.array:
            suburb = np.array(suburb, dtype=str)
        suburb = np.char.upper(suburb)

        input_df = pd.DataFrame({"suburb": suburb, "years": year_values})

        if isinstance(lga, type(None)) == False:
            if type(lga) != np.array:
                lga = np.array(lga, dtype=str)
            lga = np.char.upper(lga)
            input_df["lga"] = lga
            input_df["suburb"] = input_df.apply(
                lambda x: self._fix_double_suburbs(x["suburb"], x["lga"]), axis=1
            )
        input_df["interpolated"] = 0.0
        input_df["years"] = date_time_to_decimal_year(input_df["years"])

        for sub in input_df.suburb.unique():
            sub_mask = input_df["suburb"] == sub
            input_df.loc[sub_mask, "interpolated"] = self.get_seifa_interpolation(
                input_df.loc[sub_mask, "years"].values,
                sub,
                metric,
                _convert_data=False,
                fill_value=fill_value,
                guess_misspelt=guess_misspelt,
                **kwargs,
            )
        return input_df["interpolated"].values

    def get_gis(
        self,
        date: str,
        metric: Union[Metric, str],
        fill_value: str = "null",
    ) -> gpd.GeoDataFrame:
        """This method interpolates the metric specified to the date specified for all years, and returns a geopandas vector dataset with the metric values as a field

        Args:
            date (str): datetime that can be a year, or any datettime parseable string to interpolate map data.
            metric (Metric, or List['ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score']): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.
            fill_value (str, optional): (Union[str, np.array, tuple], optional): Specifies the values returned outside the range of the ABS census datasets. It can be "null" and return np.nan values,  "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'null'.

        Returns:
            gpd.GeoDataFrame: geodataframe of victorian suburbs with seifa score values for "metric" applied to each suburb as a column with the same name of the metric.
        """

        self._load_gis()
        if type(metric) == Metric:
            metric = metric.value

        suburbs_df = self.suburbs.copy()
        suburbs_df[metric] = self.get_seifa_interpolation_batch(
            date,
            suburbs_df["Site_suburb"].str.upper(),
            metric,
            fill_value=fill_value,
        )
        return suburbs_df

    def get_plotly_map(
        self,
        date: str,
        metric: Union[Metric, str],
        fill_value: str = "null",
        simplify: float = 0,
        min_x: Union[None, float] = None,
        min_y: Union[None, float] = None,
        max_x: Union[None, float] = None,
        max_y: Union[None, float] = None,
        clip_mask: Union[None, gpd.GeoDataFrame, gpd.GeoSeries] = None,
        **kwargs,
    ) -> plotly.graph_objects.Figure:
        """This method creates an interactive plotly choropleth map for each suburb for a give seifa score and date.


        The dataset can be simplified using the simplify command in map units, and clipped using min_x, min_y, max_x, and max_y bounds
        as well as a clipping polygons in clip mask

        Args:
            date (str): datetime that can be a year, or any datettime parseable string to interpolate map data
            metric (Metric, or List['ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score']): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.
            fill_value (Union[str, np.array, tuple], optional): Specifies the values returned outside the range of the ABS census datasets. It can be "null" and return np.nan values,  "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'null'.
            simplify (float, optional): map value to simplify polygons too according to gpd.GeoSeries.simplify method. if 0, does not simplify Defaults to 0.001.
            min_x (Union[None,float], optional):  minimum x coordinate boundary of intersecting polygons to plot. Defaults to None.
            min_y (Union[None,float], optional): maximum x coordinate boundary of intersecting polygons to plot. Defaults to None.
            max_x (Union[None,float], optional): minimum y coordinate boundary of intersecting polygons to plot Defaults to None.
            max_y (Union[None,float], optional): maximum y coordinate boundary of intersecting polygons to plot. Defaults to None.
            clip_mask (Union[None, gpd.GeoDataFrame, gpd.GeoSeries], optional): mask polygon data to clip the dataset to, overrides min_x, max_x, min_y, max_y. Defaults to None.
            kwargs (dict, option): optional additional parameters to feed into plotly.express.choropleth function.

        Returns:
            plotly.graph_objects.Figure: choropleth map of victorian suburbs with seifa_scores for each suburb
        """
        gdf = self.get_gis(date, metric, fill_value)
        return make_suburb_map(
            gdf,
            metric,
            date,
            simplify=simplify,
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            clip_mask=clip_mask,
            **kwargs,
        )

    def create_timeseries_chart(
        self,
        suburbs: Union[list, np.array, pd.Series, str],
        metric: Union[Metric, str],
        **kwargs,
    ) -> plotly.graph_objects.Figure:
        """Creates a time series of seifa metrics for a given suburb or set of suburbs as a plotly line graph

        Args:
            suburbs (Union[list, np.array, pd.Series, str]): list of suburbs to include in the time series
            metric (Union[Metric, str]): metric to plot along the time series
            kwargs (dict, optional): optional arguments to pass into plotly.express.lineplot

        Returns:
            plotly.graph_objects.Figure: plotly line plot of metric time series for a give set of suburbs
        """
        if type(metric) == Metric:
            metric = metric.value
        if type(suburbs) == str:
            suburbs = [suburbs.upper()]
        else:
            suburbs = [x.upper() for x in list(suburbs)]
        self._load_data()
        df_plot = self.df[self.df.Site_suburb.apply(lambda x: x in suburbs)].copy()
        df_plot["year"] = pd.to_datetime(df_plot["year"].apply(lambda x: f"01-01-{x}"))

        fig = create_line_plot(
            df_plot.sort_values("year"),
            x_col="year",
            y_col=metric,
            color_col="Site_suburb",
            **kwargs,
        )
        return fig


def make_suburb_map(
    gdf: gpd.GeoDataFrame,
    metric: Union[Metric, str],
    date: str = "",
    simplify: float = 0,
    min_x: Union[None, float] = None,
    min_y: Union[None, float] = None,
    max_x: Union[None, float] = None,
    max_y: Union[None, float] = None,
    clip_mask: Union[None, gpd.GeoDataFrame, gpd.GeoSeries] = None,
    **kwargs,
) -> plotly.graph_objects.Figure:
    """This function will take in a gdf and create a plotly choropleth map with the column defined by the metric argument.

    The dataset can be simplified using the simplify command in map units, and clipped using min_x, min_y, max_x, and max_y bounds
    as well as a clipping polygons in clip mask

    Args:
        gdf (gpd.GeoDataFrame): suburbs geodataframe with attached seifa scores
        metric (Metric, List['ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score']): the seifa score metric used as the color scale in the choropleth map. However it could be any column in gdf.
        date (str, optional): Date the scores were interpolated too, optional as only appears in the title if not "". Defaults to ''.
        simplify (float, optional): map scale value to simplify polygons too according to gpd.GeoSeries.simplify method. if 0, does not simplify Defaults to 0.
        min_x (Union[None,float], optional):  minimum x coordinate boundary of intersecting polygons to plot. Defaults to None.
        min_y (Union[None,float], optional): maximum x coordinate boundary of intersecting polygons to plot. Defaults to None.
        max_x (Union[None,float], optional): minimum y coordinate boundary of intersecting polygons to plot Defaults to None.
        max_y (Union[None,float], optional): maximum y coordinate boundary of intersecting polygons to plot. Defaults to None.
        clip_mask (Union[None, gpd.GeoDataFrame, gpd.GeoSeries], optional): mask polygon data to clip the dataset to, overrides min_x, max_x, min_y, max_y. Defaults to None.
        kwargs (dict, option): optional additional parameters to feed into plotly.express.choropleth function.

    Returns:
        plotly.graph_objects.Figure: choropleth map of victorian suburbs with seifa_scores for each suburb
    """
    if type(metric) == Metric:
        metric = metric.value
    if date != "":
        title = f"map for date: {date} and metric: {metric}"
    clips = [x != None for x in [min_x, min_y, max_x, max_y, clip_mask]]

    if any(clips):
        gdf = clip_gdf(gdf, min_x, max_x, min_y, max_y, clip_mask)

    fig = create_choropleth_from_geodf(
        gdf,
        metric,
        title=title,
        hover_data=["Site_suburb", metric],
        simplify=simplify,
        **kwargs,
    )
    return fig


seifa_vic = SeifaVic()


def interpolate_vic_suburb_seifa(
    year_values: Union[
        int,
        float,
        str,
        np.datetime64,
        datetime.datetime,
        np.array,
        pd.Series,
        mpd.Series,
        list,
    ],
    suburb: Union[str, np.array, list, pd.Series, mpd.Series],
    metric: Union[Metric, str],
    lga: Union[None, str, np.array, pd.Series, mpd.Series, list] = None,
    fill_value: str = "null",
    guess_misspelt: bool = False,
    **kwargs,
) -> np.array or float:
    """function to get an interpolated estimate of a SEIFA score for each victorian suburb from Australian Bureau of statistics data

    Args:
        year_values (int, float, str, datetime.datetime, np.datetime64, np.array-like): The year or array of year values you want interpolated.
        suburb (str): The name of the suburb that you want the data interpolated for (capitalisation doesn't matter).
        metric (List['ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score']): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.
        fill_value (str, np.array or tuple): Specifies the values returned outside the range of the ABS census datasets. It can be "null" and return np.nan values, "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'null'.
        guess_misspelt (bool): Tries to guess the suburb if the particular spelling is not found in the dataset. Otherwise it returns a NaN.
        **kwargs(dict-like): additional keyword arguments for scipy.interpolate.interp1D object.
    Returns:
        Union[float, np.array]: The interpolated value (s) of that seifa variable at that year(s). np.array if year_value contains multiple years.
    """
    if type(metric) == Metric:
        metric = metric.value
    if isinstance(suburb, str):
        suburb = suburb.upper()
        interpolate = seifa_vic.get_seifa_interpolation
    else:
        interpolate = seifa_vic.get_seifa_interpolation_batch

    out = interpolate(
        year_values,
        suburb,
        metric,
        lga=lga,
        fill_value=fill_value,
        guess_misspelt=guess_misspelt,
        **kwargs,
    )

    if out.size == 1:
        out = out.item()
    return out


def get_repeated_names() -> list:
    """returns the list of suburbs repeated names with their proper LGA attached

    Returns:
        list: list of repeated names, in the format of `f'{suburb} - {lga}
    """
    return seifa_vic.double_names


def get_seifa_gis(
    date: str,
    metric: Union[Metric, str],
    fill_value: str = "null",
) -> gpd.GeoDataFrame:
    """This function interpolates the metric specified to the date specified for all years, and returns a geopandas vector dataset with the metric values as a field

    Args:
        date (str): datetime that can be a year, or any datettime parseable string to interpolate map data.
        metric (Metric, or List['ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score']): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.
        fill_value (str, optional): (Union[str, np.array, tuple], optional): Specifies the values returned outside the range of the ABS census datasets. It can be "null" and return np.nan values,  "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'null'.

    Returns:
        gpd.GeoDataFrame: geodataframe of victorian suburbs with seifa score values for "metric" applied to each suburb as a column with the same name of the metric.
    """

    return seifa_vic.get_gis(date, metric, fill_value)


def get_seifa_map(
    date: str,
    metric: Union[Metric, str],
    fill_value: str = "null",
    simplify: float = 0.001,
    min_x: Union[None, float] = None,
    min_y: Union[None, float] = None,
    max_x: Union[None, float] = None,
    max_y: Union[None, float] = None,
    clip_mask: Union[None, gpd.GeoDataFrame, gpd.GeoSeries] = None,
    **kwargs,
) -> plotly.graph_objects.Figure:
    """This function creates an interactive plotly choropleth map for each suburb for a give seifa score and date.


    The dataset can be simplified using the simplify command in map units, and clipped using min_x, min_y, max_x, and max_y bounds
    as well as a clipping polygons in clip mask

    Args:
        date (str): datetime that can be a year, or any datettime parseable string to interpolate map data.
        metric (Metric, or List['ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score']): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.
        fill_value (Union[str, np.array, tuple], optional): Specifies the values returned outside the range of the ABS census datasets. It can be "null" and return np.nan values,  "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'null'.
        simplify (float, optional): map value to simplify polygons too according to gpd.GeoSeries.simplify method. if 0, does not simplify Defaults to 0.001.
        min_x (Union[None,float], optional):  minimum x coordinate boundary of intersecting polygons to plot. Defaults to None.
        min_y (Union[None,float], optional): maximum x coordinate boundary of intersecting polygons to plot. Defaults to None.
        max_x (Union[None,float], optional): minimum y coordinate boundary of intersecting polygons to plot Defaults to None.
        max_y (Union[None,float], optional): maximum y coordinate boundary of intersecting polygons to plot. Defaults to None.
        clip_mask (Union[None, gpd.GeoDataFrame, gpd.GeoSeries], optional): mask polygon data to clip the dataset to, overrides min_x, max_x, min_y, max_y. Defaults to None.
        kwargs (dict, optional): optional additional parameters to feed into plotly.express.choropleth function.

    Returns:
        plotly.graph_objects.Figure: choropleth map of victorian suburbs with seifa_scores for each suburb
    """

    return seifa_vic.get_plotly_map(
        date,
        metric,
        fill_value=fill_value,
        simplify=simplify,
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
        clip_mask=clip_mask,
        **kwargs,
    )


def create_timeseries_chart(
    suburbs: Union[list, np.array, pd.Series, str], metric: Union[Metric, str], **kwargs
) -> plotly.graph_objects.Figure:
    """Creates a time series of seifa metrics for a given suburb or set of suburbs as a plotly line graph

    Args:
        suburbs (Union[list, np.array, pd.Series, str]): list of suburbs to include in the time series
        metric (Union[Metric, str]): metric to plot along the time series
        kwargs (dict, optional): optional arguments to pass into plotly.express.lineplot

    Returns:
        plotly.graph_objects.Figure: plotly line plot of metric time series for a give set of suburbs
    """
    fig = seifa_vic.create_timeseries_chart(suburbs, metric, **kwargs)
    return fig
