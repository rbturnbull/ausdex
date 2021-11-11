from dateutil import parser
from typing import Union
import numpy as np
import pandas as pd
import modin.pandas as mpd
from datetime import datetime


def convert_date(date: Union[datetime, str, pd.Series, np.ndarray]) -> np.ndarray:
    """Receives `date` from a variety of datatypes and converts it into a numeric value in a numpy array.

    If `date` is a string then it is converted to a datetime using dateutil.parser.
    If `date` is a vector then it returns a vector otherwise it returns a single scalar value.

    Args:
        date (Union[datetime, str, pd.Series, np.ndarray]): The date to be converted

    Returns:
        np.ndarray: A numerical form of the date.
    """
    if type(date) == str:
        date = parser.parse(date)
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
        return date
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
