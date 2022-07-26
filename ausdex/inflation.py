from datetime import datetime
from typing import Union
import pandas as pd
import modin.pandas as mpd
import numpy as np
import numbers

from cached_property import cached_property

from .location import Location
from .files import cached_download_cpi
from .dates import convert_date


class CPI:
    """A class to manage the Australian Consumer Index (CPI) data."""

    @cached_property
    def latest_cpi_df(self) -> pd.DataFrame:
        """
        Returns a Pandas DataFrame with the latest Australian Consumer Price Index (CPI) data.

        Returns:
            pd.DataFrame: The latest Australian Consumer Price Index (CPI) data. The index of the series is the relevant date for each row.
        """
        local_path = cached_download_cpi()
        excel_file = pd.ExcelFile(local_path)
        df = excel_file.parse("Data1")

        # Get rid of extra headers
        df = df.iloc[9:]

        df = df.rename(columns={"Unnamed: 0": "Date"})
        df.index = df["Date"]

        return df

    def column_name(self, location: Union[Location, str] = Location.AUSTRALIA):
        return f"Index Numbers ;  All groups CPI ;  {str(location).title()} ;"

    def cpi_series(self, location: Union[Location, str] = Location.AUSTRALIA) -> pd.Series:
        """
        Returns a Pandas Series with the Australian CPI (Consumer Price Index) per quarter.

        This is taken from the latest spreadsheet from the Australian Bureau of Statistics (file id '640101').
        The index of the series is the relevant date.

        Args:
            location (Union[Location, str], optional): The location for calculating the CPI.
                Options are 'Australia', 'Sydney', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin', and 'Canberra'.
                Default is 'Australia'.

        Returns:
            pd.Series: The CPIs per quarter.
        """
        df = self.latest_cpi_df

        return df[self.column_name(location)]

    def cpi_at(
        self, date: Union[datetime, str, pd.Series, np.ndarray], location: Union[Location, str] = Location.AUSTRALIA
    ) -> Union[float, np.ndarray]:
        """
        Returns the CPI (Consumer Price Index) for a date (or a number of dates).

        If `date` is a string then it is converted to a datetime using dateutil.parser.
        If `date` is a vector then it returns a vector otherwise it returns a single scalar value.
        If `date` is before the earliest reference date (i.e. 1948-09-01) then it returns a NaN.

        Args:
            date (Union[datetime, str, pd.Series, np.ndarray]): The date(s) to get the CPI(s) for.
            location (Union[Location, str], optional): The location for calculating the CPI.
                Options are 'Australia', 'Sydney', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin', and 'Canberra'.
                Default is 'Australia'.

        Returns:
            Union[float, np.ndarray]: The CPI value(s).
        """
        date = convert_date(date)

        cpi_series = self.cpi_series(location=location)

        min_date = cpi_series.index.min()
        cpis = np.array(
            cpi_series[np.searchsorted(cpi_series.index, date, side="right") - 1],
            dtype=float,
        )
        cpis[date < min_date] = np.nan

        # TODO check if the date difference is greater than 3 months

        if cpis.size == 1:
            return cpis.item()

        return cpis

    def calc_inflation(
        self,
        value: Union[numbers.Number, np.ndarray, pd.Series],
        original_date: Union[datetime, str],
        evaluation_date: Union[datetime, str, None] = None,
        location: Union[Location, str] = Location.AUSTRALIA,
    ):
        """
        Adjusts a value (or list of values) for inflation.

        Args:
            value (Union[numbers.Number, np.ndarray, pd.Series]): The value to be converted.
            original_date (Union[datetime, str]): The date that the value is in relation to.
            evaluation_date (Union[datetime, str], optional): The date to adjust the value to. Defaults to the current date.
            location (Union[Location, str], optional): The location for calculating the CPI.
                Options are 'Australia', 'Sydney', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin', and 'Canberra'.
                Default is 'Australia'.

        Returns:
            Union[float, np.ndarray]: The adjusted value.
        """
        if evaluation_date is None:
            evaluation_date = datetime.now()

        original_cpi = self.cpi_at(original_date, location=location)
        evaluation_cpi = self.cpi_at(evaluation_date, location=location)
        return value * evaluation_cpi / original_cpi

    def calc_inflation_timeseries(
        self,
        compare_date: Union[datetime, str],
        start_date: Union[datetime, str, None] = None,
        end_date: Union[datetime, str, None] = None,
        value=1,
        location: Union[Location, str] = Location.AUSTRALIA,
    ) -> pd.Series:
        compare_date = convert_date(compare_date)
        if start_date != None:
            start_date = convert_date(start_date).item()
        if end_date != None:
            end_date = convert_date(end_date).item()

        cpi_ts = self.cpi_series(location=location)[start_date:end_date].copy()
        evaluation_cpi = self.cpi_at(compare_date, location=location)
        inflation = value * (evaluation_cpi / cpi_ts)
        return inflation


_cpi = CPI()


def calc_inflation(
    value: Union[numbers.Number, np.ndarray, pd.Series],
    original_date: Union[datetime, str],
    evaluation_date: Union[datetime, str] = None,
    location: Union[Location, str] = Location.AUSTRALIA,
) -> Union[float, np.ndarray]:
    """
    Adjusts a value (or list of values) for inflation.

    Args:
        value (numbers.Number, np.ndarray, pd.Series): The value to be converted.
        original_date (datetime, str): The date that the value is in relation to.
        evaluation_date (datetime, str, optional): The date to adjust the value to. Defaults to the current date.
        location (Location, str, optional): The location for calculating the CPI.
            Options are 'Australia', 'Sydney', 'Melbourne', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Darwin', and 'Canberra'.
            Default is 'Australia'.

    Returns:
        Union[float, np.ndarray]: The adjusted value.
    """
    return _cpi.calc_inflation(
        value,
        original_date=original_date,
        evaluation_date=evaluation_date,
        location=location,
    )


def latest_cpi_df() -> pd.DataFrame:
    """
    Returns a pandas DataFrame with the latest CPI data from the Australian Bureau of Statistics.

    This will contain the data for each quarter going back to 1948.

    Returns:
        pandas.DataFrame: The latest dataframe with the CPI data.

    """
    return _cpi.latest_cpi_df
