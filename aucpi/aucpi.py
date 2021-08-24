from datetime import datetime
from pathlib import Path
from appdirs import user_cache_dir
import pandas as pd
from dateutil import parser
import numpy as np

from cached_property import cached_property

from aucpi.files import cached_download

class Aucpi():
    ACCEPTED_QUARTERS = ["mar", "jun", "sep", "dec"]

    def get_abs(self, id, quarter, year):
        quarter = quarter.lower()[:3]
        if quarter not in self.ACCEPTED_QUARTERS:
            raise ValueError(f"Cannot understand quarter {quarter}.")
        
        url = f"https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/{quarter}-{year}/{id}.xls"

        cache_dir = Path(user_cache_dir("aucpi"))
        cache_dir.mkdir(exist_ok=True, parents=True)
        local_path = cache_dir/f"{id}-{quarter}-{year}.xls"

        cached_download(url, local_path)
        return local_path


    def get_640101(self, quarter, year):
        return self.get_abs("640101", quarter, year)

    def latest_640101(self):
        # HACK. should get quarter and year dynamically
        quarter = "jun"
        year = 2021
        return self.get_640101(quarter, year)

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
        """ Returns a pandas series with the Australian CPI indexes per quarter"""
        df = self.latest_df
        return df['Index Numbers ;  All groups CPI ;  Australia ;']

    def cpi_australia_at(self, date: (datetime,str)):
        if type(date) == str:
            date = parser.parse(date)
        try:
            return self.cpi_australia_series[self.cpi_australia_series.index <= date].iloc[-1]
        except:
            raise ValueError(f"Cannot get CPI for date '{date}'")

    def adjust( self, value, original_date: (datetime,str), evaluation_date: (datetime,str) = None ):
        """ Adjusts a value for inflation. """
        try:
            evaluation_date = evaluation_date or datetime.now()

            original_cpi = self.cpi_australia_at(original_date)
            evaluation_cpi = self.cpi_australia_at(evaluation_date)
            return value * evaluation_cpi/original_cpi
        except:
            return np.nan


aucpi = Aucpi()
def adjust(value, original_date: (datetime,str), evaluation_date: (datetime,str) = None):
    """ Adjusts a value for inflation. """
    return aucpi.adjust(value, original_date=original_date, evaluation_date=evaluation_date)