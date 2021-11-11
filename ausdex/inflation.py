import sys
from datetime import datetime, timedelta
from typing import Union
import pandas as pd
import modin.pandas as mpd
from dateutil import parser
import numpy as np
import numbers

from cached_property import cached_property

from .files import cached_download, get_cached_path


class CPI:
    ACCEPTED_QUARTERS = ["mar", "jun", "sep", "dec"]

    def get_abs(self, id, quarter, year):
        """Gets a CPI datafile from the Australian Burau of Statistics."""
        quarter = quarter.lower()[:3]
        if quarter not in self.ACCEPTED_QUARTERS:
            raise ValueError(f"Cannot understand quarter {quarter}.")

        url = f"https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/{quarter}-{year}/{id}.xls"

        local_path = get_cached_path(f"{id}-{quarter}-{year}.xls")

        cached_download(url, local_path)
        return local_path

    def get_abs_by_date(self, id: str, date: datetime):
        """Gets the latest CPI datafile from the Australian Burau of Statistics before a specific date."""
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

    def latest_640101(self):
        return self.get_abs_by_date("640101", datetime.now())

    @cached_property
    def latest_df(self) -> pd.DataFrame:
        local_path = self.latest_640101()
        excel_file = pd.ExcelFile(local_path)
        df = excel_file.parse("Data1")

        # Get rid of extra headers
        df = df.iloc[9:]

        df = df.rename(columns={"Unnamed: 0": "Date"})
        df.index = df["Date"]

        return df

    @cached_property
    def cpi_australia_series(self) -> pd.Series:
        """Returns a pandas series with the Australian CPI indexes per quarter"""
        df = self.latest_df
        return df["Index Numbers ;  All groups CPI ;  Australia ;"]

    def cpi_australia_at(self, date: Union[datetime, str, pd.Series, np.ndarray]):
        """
        Returns the CPI for dates.

        If `date` is a string then it is converted to a datetime using dateutil.parser.
        If `date` is a vector then it returns a vector otherwise it returns a single scalar value.
        If `date` is before the earliest reference date (i.e. 1948-09-01) then it returns a NaN.
        """
        if type(date) == str:
            date = parser.parse(date)
        elif type(date) == mpd.Series:
            date = mpd.to_datetime(date)
        else:
            date = pd.to_datetime(date)

        dates = np.array(date, dtype="datetime64[D]")
        min_date = self.cpi_australia_series.index.min()
        cpis = np.array(
            self.cpi_australia_series[
                np.searchsorted(self.cpi_australia_series.index, date, side="right") - 1
            ],
            dtype=float,
        )
        cpis[dates < min_date] = np.nan

        if cpis.size == 1:
            return cpis.item()

        return cpis

    def calc_inflation(
        self,
        value: (numbers.Number, np.ndarray, pd.Series),
        original_date: (datetime, str),
        evaluation_date: (datetime, str) = None,
    ):
        """Adjusts a value for inflation."""
        if evaluation_date is None:
            evaluation_date = datetime.now()

        original_cpi = self.cpi_australia_at(original_date)
        evaluation_cpi = self.cpi_australia_at(evaluation_date)
        return value * evaluation_cpi / original_cpi


_cpi = CPI()


def calc_inflation(
    value: (numbers.Number, np.ndarray, pd.Series),
    original_date: (datetime, str),
    evaluation_date: (datetime, str) = None,
):
    """Adjusts a value for inflation."""
    return _cpi.calc_inflation(
        value, original_date=original_date, evaluation_date=evaluation_date
    )
