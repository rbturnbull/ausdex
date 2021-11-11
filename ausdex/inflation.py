import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Union
import pandas as pd
import modin.pandas as mpd
from dateutil import parser
import numpy as np
import numbers

from cached_property import cached_property

from .files import cached_download, get_cached_path
from .dates import convert_date


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
