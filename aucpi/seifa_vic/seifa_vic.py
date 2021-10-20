from aucpi import seifa_vic
from .data_wrangling import preprocess_victorian_datasets
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd
from typing import Union
import enum

metrics = [
    "ier_score",
    "irsd_score",
    "ieo_score",
    "irsad_score",
    "rirsa_score",
    "uirsa_score",
]
Metric = enum.Enum("Metric", {metric: metric for metric in metrics})


class SeifaVic:
    """This object loads, or creates the combined dataset for the SEIFA_VIC interpolations"""

    def __init__(self, force_rebuild=False):
        """initialising SeifaVic object

        Args:
                force_rebuild (bool, optional): forces the reconstruction of the combined dataset if already built and saved in user data. Defaults to False.
        """
        self.force_rebuild = force_rebuild

    def _load_data(self):
        """loads the preprocessed victorian dataset if it hasn't been loaded already"""
        if "df" not in self.__dict__:
            # print('loading data')
            self.df = preprocess_victorian_datasets(force_rebuild=self.force_rebuild)

    def get_suburb_data(self, suburb: str):
        """
        returns the dataset (self.df) filtered to a suburb

        Args:
                suburb (str): suburb that dataset will be filtered to.

        Returns:
                pd.DataFrame: filtered dataframe with only the data from that suburb
        """
        result = self.df[self.df["Site_suburb"] == suburb.upper()]

        if len(result) == 0:
            raise ValueError(f"No data for suburb: '{suburb}'.")

        return result

    def build_interpolator(
        self,
        suburb: str,
        metric: str,
        fill_value: Union[str, np.array, tuple],
        **kwargs,
    ) -> interp1d:
        """
        Builds an interpolator with the "year" column as the x, and the metric column as the y.

        Args:
                suburb (str): suburb that dataset will be filtered too(must be all caps)
                metric (str): 'ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score', the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.

                fill_value (Union[str, np.array, tuple]): Specifies the values returned outside the range of the ABS census datasets. It can be "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument.

        Returns:
                scipy.interpolate.interp1d: interpolator object for the suburb and metric
        """

        if metric not in metrics:
            raise ValueError(f"Metric {metric} not available. Choose from: {metrics}.")

        df = self.get_suburb_data(suburb).dropna(subset=[metric]).sort_values("year")
        if fill_value == "boundary_value":

            fill_value = (df[metric].values[0], df[metric].values[-1])

        kwargs["bounds_error"] = False
        return interp1d(
            df["year"].values, df[metric].values, fill_value=fill_value, **kwargs
        )

    def get_seifa_interpolation(
        self,
        year_values: Union[int, float, np.array, list],
        suburb: str,
        metric: str,
        fill_value: Union[str, np.array, tuple] = "extrapolate",
        **kwargs,
    ) -> Union[float, np.array]:
        """
        Gets an interpolated estimate of a SEIFA score for each victorian suburb from Australian Bureau of statistics data.

        Args:
                year_values (Union[int,float,np.array, list]): The year or array of year values you want interpolated.
                suburb (str): The name of the suburb that you want the data interpolated for (capitalisation doesn't matter).
                metric (str): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.
                fill_value (Union[str, np.array, tuple], optional): Specifies the values returned outside the range of the ABS census datasets. It can be "extrapolate" to extraplate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'extrapolate'.
                **kwargs(dict-like): additional keyword arguments for scipy.interpolate.interp1D object.

        Returns:
                Union[float, np.array]: The interpolated value (s) of that seifa variable at that year(s). np.array if year_value contains multiple years.
        """
        assert isinstance(
            year_values, (int, float, list, np.float32, np.int32, np.array, pd.Series)
        )
        self._load_data()
        return self.build_interpolator(suburb, metric, fill_value=fill_value, **kwargs)(
            year_values
        )


seifa_vic = SeifaVic()


def interpolate_vic_suburb_seifa(
    year_values, suburb, metric, fill_value="extrapolate", **kwargs
) -> np.array or float:
    """
        Gets an interpolated estimate of a SEIFA score for each victorian suburb from Australian Bureau of statistics data.

    Args:
            year_values (int, float, np.ndarray like): The year or array of year values you want interpolated.
            suburb (str): The name of the suburb that you want the data interpolated for (capitalisation doesn't matter).
            metric (List['ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score']): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.
            fill_value (str, np.array or tuple): Specifies the values returned outside the range of the ABS census datasets. It can be "extrapolate" to extraplate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'extrapolate'.
            **kwargs(dict-like): additional keyword arguments for scipy.interpolate.interp1D object.
    Returns:
            Union[float, np.array]: The interpolated value (s) of that seifa variable at that year(s). np.array if year_value contains multiple years.
    """

    out = seifa_vic.get_seifa_interpolation(
        year_values, suburb, metric, fill_value=fill_value, **kwargs
    )
    if out.size == 1:
        out = out.item()
    return out
