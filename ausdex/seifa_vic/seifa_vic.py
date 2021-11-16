from pandas.core.arrays.sparse import dtype
from ausdex import seifa_vic
from .data_wrangling import preprocess_victorian_datasets
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd
import datetime
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from ..dates import date_time_to_decimal_year
from typing import Union
import enum
import modin.pandas as mpd

DOUBLE_NAMES = [
    "ASCOT - BALLARAT",
    "ASCOT - GREATER BENDIGO",
    "ASCOT - HEPBURN",
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
        **kwargs,
    ) -> interp1d:
        """this function builds an interpolator with the "year" column as the x, and the metric column as the y

        Args:
            suburb (str): suburb that dataset will be filtered too(must be all caps)
            metric (str): 'ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score', the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.

            fill_value (Union[str, np.array, tuple]): Specifies the values returned outside the range of the ABS census datasets. It can be "null" to return np.nan values, "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument.

        Returns:
            scipy.interpolate.interp1d: interpolator object for the suburb and metric
        """
        df = self.get_suburb_data(suburb).dropna(subset=[metric]).sort_values("year")
        if fill_value == "boundary_value":

            fill_value = (df[metric].values[0], df[metric].values[-1])
        elif fill_value == "null":
            fill_value = (np.nan, np.nan)
        kwargs["bounds_error"] = False
        if df.shape[0] > 1:
            return interp1d(
                df["year"].values, df[metric].values, fill_value=fill_value, **kwargs
            )
        else:
            print(f"no suburb anmed {suburb}")
            return _make_nan

    def get_interpolator(
        self,
        suburb: str,
        metric: str,
        fill_value: Union[str, np.array, tuple],
        **kwargs,
    ) -> interp1d:
        cache_name = _make_cache_key(suburb, metric, fill_value, **kwargs)
        if cache_name not in self.interp_cache:

            self.interp_cache[cache_name] = self.build_interpolator(
                suburb, metric, fill_value=fill_value, **kwargs
            )
        return self.interp_cache[cache_name]

    def get_seifa_interpolation(
        self,
        year_values: Union[int, float, np.array, list],
        suburb: str,
        metric: str,
        lga: Union[str, None] = None,
        fill_value: Union[str, np.array, tuple] = "null",
        _convert_data=True,
        **kwargs,
    ) -> Union[float, np.array]:
        """method to get an interpolated estimate of a SEIFA score for each victorian suburb from Australian Bureau of statistics data

        Args:
            year_values (Union[int,float,np.array, list]): The year or array of year values you want interpolated.
            suburb (str): The name of the suburb that you want the data interpolated for (capitalisation doesn't matter).
            metric (str): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.
            fill_value (Union[str, np.array, tuple], optional): Specifies the values returned outside the range of the ABS census datasets. It can be "null" and return np.nan values,  "extrapolate" to extraplate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'null'.
            _convert_data (bool): if true, will convert datetime values to decimal years, only false when batching
            **kwargs(dict-like): additional keyword arguments for scipy.interpolate.interp1D object.

        Returns:
            Union[float, np.array]: The interpolated value (s) of that seifa variable at that year(s). np.array if year_value contains multiple years.
        """
        self._load_data()

        if _convert_data == True:
            year_values = date_time_to_decimal_year(year_values)

        if type(lga) == str:
            suburb = self._fix_double_suburbs(
                suburb.upper().strip(), lga.upper().strip()
            )

        return self.get_interpolator(suburb, metric, fill_value=fill_value, **kwargs)(
            year_values
        )

    def get_seifa_interpolation_batch(
        self,
        year_values: Union[int, float, np.array, np.datetime64, list],
        suburb: Union[list, np.array, pd.Series, mpd.Series],
        metric: str,
        lga: Union[list, np.array, pd.Series, mpd.Series, None] = None,
        fill_value: Union[str, np.array, tuple] = "null",
        **kwargs,
    ) -> Union[float, np.array]:

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
                **kwargs,
            )

        return input_df["interpolated"].values


seifa_vic = SeifaVic()


def interpolate_vic_suburb_seifa(
    year_values, suburb, metric, lga=None, fill_value="null", **kwargs
) -> np.array or float:
    """function to get an interpolated estimate of a SEIFA score for each victorian suburb from Australian Bureau of statistics data

    Args:
        year_values (int, float, np.ndarray like): The year or array of year values you want interpolated.
        suburb (str): The name of the suburb that you want the data interpolated for (capitalisation doesn't matter).
        metric (List['ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score']): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage.
        fill_value (str, np.array or tuple): Specifies the values returned outside the range of the ABS census datasets. It can be "null" and return np.nan values, "extrapolate" to extraplate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'null'.
        **kwargs(dict-like): additional keyword arguments for scipy.interpolate.interp1D object.
    Returns:
        Union[float, np.array]: The interpolated value (s) of that seifa variable at that year(s). np.array if year_value contains multiple years.
    """
    if type(suburb) == str:
        out = seifa_vic.get_seifa_interpolation(
            year_values,
            suburb.upper(),
            metric,
            lga=lga,
            fill_value=fill_value,
            **kwargs,
        )
    else:
        out = seifa_vic.get_seifa_interpolation_batch(
            year_values, suburb, metric, lga=lga, fill_value=fill_value, **kwargs
        )
    if out.size == 1:
        out = out.item()
    return out
