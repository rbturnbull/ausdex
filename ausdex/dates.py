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
        if np.issubdtype(date.dtype, np.integer):
            date = date.astype(str)
        date = pd.to_datetime(date)
    elif type(date) == mpd.Series:
        date = mpd.to_datetime(date)
    else:
        date = pd.to_datetime(date)

    return np.array(date, dtype="datetime64[D]")


def _dt_to_dyr(x):
    return float(x.year + x.month / 12 + x.day / 30)


def date_time_to_decimal_year(
    date: Union[
        datetime, pd.Timestamp, np.datetime64, int, float, str, pd.Series, np.ndarray
    ]
) -> np.ndarray:

    if isinstance(date, (float, int)):
        return np.array([date])
    elif isinstance(date, (datetime, pd.Timestamp, np.datetime64)):
        return _dt_to_dyr(pd.to_datetime(date))

    elif isinstance(date, (pd.Series, np.ndarray)):
        if date.dtype in [float, int]:
            return date
    else:
        return _dt_to_dyr(pd.to_datetime(convert_date(date)))

    if type(x) != pd.Timestamp:
        x = pd.TimeStamp(x)
    return _dt_to_dyr(x)
