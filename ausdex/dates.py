from typing import Union
import numpy as np
import pandas as pd
import modin.pandas as mpd
from datetime import datetime, timedelta
import calendar


def convert_date(date: Union[datetime, str, pd.Series, np.ndarray]) -> np.ndarray:
    """Receives `date` from a variety of datatypes and converts it into a numeric value in a numpy array.

    If `date` is a vector then it returns a vector otherwise it returns a single scalar value.

    Args:
        date (Union[datetime, str, pd.Series, np.ndarray]): The date to be converted

    Returns:
        np.ndarray: A numerical form of the date.
    """
    if isinstance(date, int):
        date = pd.to_datetime(str(date))
    elif isinstance(date, float):
        year = int(date)
        days_in_year = 366 if calendar.isleap(year) else 365
        date = datetime(year, 1, 1) + timedelta(days=(date % 1) * days_in_year)
    elif isinstance(date, np.ndarray):
        date = pd.to_datetime(date.astype(str))
    elif type(date) == mpd.Series:
        date = mpd.to_datetime(date)
    else:
        date = pd.to_datetime(date)

    return np.array(date, dtype="datetime64[D]")
