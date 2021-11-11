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
