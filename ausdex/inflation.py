import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Union
import pandas as pd
from pandas._config import config
import modin.pandas as mpd
from dateutil import parser
import numpy as np
import numbers
import plotly

from cached_property import cached_property

from .files import cached_download, get_cached_path
from .dates import convert_date
from .data_viz import create_line_plot


class CPI:
    """A class to manage the Australian Consumer Index (CPI) data."""

    ACCEPTED_QUARTERS = ["mar", "jun", "sep", "dec"]

    def get_abs(self, id: str, quarter: str, year: Union[str, int]) -> Path:
        """Gets a datafile from the Australian Burau of Statistics.

        Args:
            id (str): The ABS id for the datafile. For Australian Consumer Price Index the ID is 640101.
            quarter (str): One of "mar", "jun", "sep", or "dec".
            year (Union[str,int]): [description]

        Raises:
            ValueError: Raises this error if the quarter cannot be understood.

        Returns:
            Path: The path to the cached ABS datafile
        """
        quarter = quarter.lower()[:3]
        if quarter not in self.ACCEPTED_QUARTERS:
            raise ValueError(f"Cannot understand quarter {quarter}.")

        url = f"https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/{quarter}-{year}/{id}.xls"

        local_path = get_cached_path(f"{id}-{quarter}-{year}.xls")

        cached_download(url, local_path)
        return local_path

    def get_abs_by_date(self, id: str, date: datetime) -> Path:
        """Gets a datafile from the Australian Burau of Statistics before a specific date.

        Args:
            id (str): The ABS id for the datafile. For Australian Consumer Price Index (CPI) the ID is 640101.
            date (datetime): The date before which the CPI data should be valid.

        Returns:
            Path: The path to the cached ABS datafile.
        """
        file = None
        while file is None and date > datetime(1948, 1, 1):
            try:
                year = date.year
                quarter_index = (date.month - 3) // 3
                if quarter_index == -1:
                    quarter_index = 3
                    year -= 1
                quarter = self.ACCEPTED_QUARTERS[quarter_index]

                file = self.get_abs(id, quarter, year)
            except:
                print(f"CPI data for {date} not available.", file=sys.stderr)

            date -= timedelta(days=89)  # go back approximately a quarter

        return file

    def latest_cpi_datafile(self) -> Path:
        """Returns the path to the latest cached file with the Australian Consumer Price Index (CPI) data.

        The ABS id of this file is "640101".

        Returns:
            Path: The path to the cached datafile.
        """
        return self.get_abs_by_date("640101", datetime.now())

    @cached_property
    def latest_cpi_df(self) -> pd.DataFrame:
        """Returns a Pandas DataFrame with the latest Australian Consumer Price Index (CPI) data.

        Returns:
            pd.DataFrame: The latest Australian Consumer Price Index (CPI) data. The index of the series is the relevant date for each row.
        """
        local_path = self.latest_cpi_datafile()
        excel_file = pd.ExcelFile(local_path)
        df = excel_file.parse("Data1")

        # Get rid of extra headers
        df = df.iloc[9:]

        df = df.rename(columns={"Unnamed: 0": "Date"})
        df.index = df["Date"]

        return df

    @cached_property
    def cpi_australia_series(self) -> pd.Series:
        """Returns a Pandas Series with the Australian CPI (Consumer Price Index) per quarter.

        This is taken from the latest spreadsheet from the Australian Bureau of Statistics (file id '640101'). The index of the series is the relevant date.

        Returns:
            pd.Series: The CPIs per quarter.
        """
        df = self.latest_cpi_df
        return df["Index Numbers ;  All groups CPI ;  Australia ;"]

    def cpi_australia_at(
        self, date: Union[datetime, str, pd.Series, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """Returns the CPI (Consumer Price Index) for a date (or a number of dates).

        If `date` is a string then it is converted to a datetime using dateutil.parser.
        If `date` is a vector then it returns a vector otherwise it returns a single scalar value.
        If `date` is before the earliest reference date (i.e. 1948-09-01) then it returns a NaN.

        Args:
            date (Union[datetime, str, pd.Series, np.ndarray]): The date(s) to get the CPI(s) for.

        Returns:
            Union[float, np.ndarray]: The CPI value(s).
        """
        date = convert_date(date)

        min_date = self.cpi_australia_series.index.min()
        cpis = np.array(
            self.cpi_australia_series[
                np.searchsorted(self.cpi_australia_series.index, date, side="right") - 1
            ],
            dtype=float,
        )
        cpis[date < min_date] = np.nan

        if cpis.size == 1:
            return cpis.item()

        return cpis

    def calc_inflation(
        self,
        value: Union[numbers.Number, np.ndarray, pd.Series],
        original_date: Union[datetime, str],
        evaluation_date: Union[datetime, str] = None,
    ):
        """Adjusts a value (or list of values) for inflation.

        Args:
            value (Union[numbers.Number, np.ndarray, pd.Series]): The value to be converted.
            original_date (Union[datetime, str]): The date that the value is in relation to.
            evaluation_date (Union[datetime, str], optional): The date to adjust the value to. Defaults to the current date.

        Returns:
            Union[float, np.ndarray]: The adjusted value.
        """
        if evaluation_date is None:
            evaluation_date = datetime.now()

        original_cpi = self.cpi_australia_at(original_date)
        evaluation_cpi = self.cpi_australia_at(evaluation_date)
        return value * evaluation_cpi / original_cpi

    def calc_inflation_timeseries(
        self,
        compare_date: Union[datetime, str],
        start_date: Union[datetime, str, None] = None,
        end_date: Union[datetime, str, None] = None,
        value=1,
    ) -> pd.Series:
        compare_date = convert_date(compare_date)
        if start_date != None:
            start_date = convert_date(start_date).item()
        if end_date != None:
            end_date = convert_date(end_date).item()

        cpi_ts = self.cpi_australia_series[start_date:end_date].copy()
        evaluation_cpi = self.cpi_australia_at(compare_date)
        inflation = value * (evaluation_cpi / cpi_ts)
        return inflation

    def plot_inflation_timeseries(
        self,
        compare_date: Union[datetime, str],
        start_date: Union[datetime, str, None] = None,
        end_date: Union[datetime, str, None] = None,
        value: Union[float, int] = 1,
        **kwargs,
    ) -> plotly.graph_objects.Figure:
        """method plot a time series of dollar values attached to a particular date's dollar value

        Args:
            compare_date (Union[datetime, str]): Date to set relative value of the dollars too.
            start_date (Union[datetime, str, None], optional): Date to set the beginning of the time series graph. Defaults to None, which starts in 1948.
            end_date (Union[datetime, str, None], optional): Date to set the end of the time series graph too. Defaults to None, which will set the end date to the most recent quarter.
            value (Union[float, int], optional): Value you in `compare_date` dollars to plot on the time series. Defaults to 1.
            kwargs: (Optional(dict)): additional parameters to feed into plotly.express.line function

        Returns:
            plotly.graph_objects.Figure: line graph of inflated dollar values vs time
        """

        inflation = self.calc_inflation_timeseries(
            compare_date, start_date, end_date, value=value
        ).reset_index()
        new_col_name = f"price of $ {value} in {str(compare_date)} dollars"
        if "title" not in kwargs:
            kwargs[
                "title"
            ] = f"Inflation time series for ${value} at evaluated in {str(compare_date)} dollars"
        inflation.rename(
            columns={"Index Numbers ;  All groups CPI ;  Australia ;": new_col_name},
            inplace=True,
        )
        fig = create_line_plot(
            inflation, x_col="Date", y_col=new_col_name, color_col=None, **kwargs
        )
        return fig

    def plot_cpi_timeseries(
        self,
        start_date: Union[datetime, str, None] = None,
        end_date: Union[datetime, str, None] = None,
        **kwargs,
    ) -> plotly.graph_objects.Figure:
        """method to plot the Australian CPI vs time

        Args:
            start_date (Union[datetime, str, None], optional): Date to set the beginning of the time series graph. Defaults to None, which starts in 1948.
            end_date (Union[datetime, str, None], optional): Date to set the end of the time series graph too. Defaults to None, which will set the end date to the most recent quarter.
            kwargs: (Optional(dict)): additional parameters to feed into plotly.express.line function

        Returns:
            plotly.graph_objects.Figure: plot of cpi vs time
        """
        if start_date != None:
            start_date = convert_date(start_date).item()
        if end_date != None:
            end_date = convert_date(end_date).item()
        cpi_ts = self.cpi_australia_series[start_date:end_date].copy()
        cpi_ts = cpi_ts.reset_index()
        cpi_ts.rename(
            columns={
                "Index Numbers ;  All groups CPI ;  Australia ;": "Australian Consumer Price Index"
            },
            inplace=True,
        )
        if "title" not in kwargs:
            kwargs["title"] = f"Australian Consumer Price Index time series"
        fig = create_line_plot(
            cpi_ts,
            x_col="Date",
            y_col="Australian Consumer Price Index",
            color_col=None,
            **kwargs,
        )
        return fig


_cpi = CPI()


def calc_inflation(
    value: Union[numbers.Number, np.ndarray, pd.Series],
    original_date: Union[datetime, str],
    evaluation_date: Union[datetime, str] = None,
) -> Union[float, np.ndarray]:
    """Adjusts a value (or list of values) for inflation.

    Args:
        value (Union[numbers.Number, np.ndarray, pd.Series]): The value to be converted.
        original_date (Union[datetime, str]): The date that the value is in relation to.
        evaluation_date (Union[datetime, str], optional): The date to adjust the value to. Defaults to the current date.

    Returns:
        Union[float, np.ndarray]: The adjusted value.
    """
    return _cpi.calc_inflation(
        value,
        original_date=original_date,
        evaluation_date=evaluation_date,
    )


def plot_inflation_timeseries(
    compare_date: Union[datetime, str],
    start_date: Union[datetime, str, None] = None,
    end_date: Union[datetime, str, None] = None,
    value: Union[float, int] = 1,
    **kwargs,
) -> plotly.graph_objects.Figure:
    """function to plot a time series of dollar values attached to a particular date's dollar value

    Args:
        compare_date (Union[datetime, str]): Date to set relative value of the dollars too.
        start_date (Union[datetime, str, None], optional): Date to set the beginning of the time series graph. Defaults to None, which starts in 1948.
        end_date (Union[datetime, str, None], optional): Date to set the end of the time series graph too. Defaults to None, which will set the end date to the most recent quarter.
        value (Union[float, int], optional): Value you in `compare_date` dollars to plot on the time series. Defaults to 1.
        kwargs: (Optional(dict)): additional parameters to feed into plotly.express.line function

    Returns:
        plotly.graph_objects.Figure: line graph of inflated dollar values vs time
    """
    return _cpi.plot_inflation_timeseries(
        compare_date, start_date=start_date, end_date=end_date, value=value, **kwargs
    )


def plot_cpi_timeseries(
    start_date: Union[datetime, str, None] = None,
    end_date: Union[datetime, str, None] = None,
    **kwargs,
) -> plotly.graph_objects.Figure:
    """function to plot the Australian CPI vs time

    Args:
        start_date (Union[datetime, str, None], optional): Date to set the beginning of the time series graph. Defaults to None, which starts in 1948.
        end_date (Union[datetime, str, None], optional): Date to set the end of the time series graph too. Defaults to None, which will set the end date to the most recent quarter.
        kwargs: (Optional(dict)): additional parameters to feed into plotly.express.line function

    Returns:
        plotly.graph_objects.Figure: plot of cpi vs time
    """
    return _cpi.plot_cpi_timeseries(start_date=start_date, end_date=end_date, **kwargs)
