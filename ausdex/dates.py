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
        np.ndarray: A NumPy array with datatype datetime64[D].
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


def timestamp_to_decimal_year(date):
    return np.array(date.year + (date.dayofyear - 1) / (365.0 + date.is_leap_year * 1.0))


def date_time_to_decimal_year(
    date: Union[
        datetime,
        pd.Timestamp,
        list,
        tuple,
        np.datetime64,
        int,
        float,
        str,
        pd.Series,
        np.ndarray,
    ]
) -> np.ndarray:
    """
    Converts a date from a variety of formats to be a decimal year.

    Args:
        date (Union[ datetime, pd.Timestamp, list, tuple, np.datetime64, int, float, str, pd.Series, np.ndarray, ]):
            The date to be converted.

    Returns:
        np.ndarray: The date as a NumPy array of the same shape as the input.
    """
    # If the date is a list or a tuple, then convert to a numpy array before doing anything else
    if isinstance(date, (list, tuple)):
        date = np.array(date)

    if isinstance(date, (float, int)):
        # if a scalar numerical value, then assume that this is already as a numerical date
        return np.array([date])
    elif isinstance(date, (datetime, pd.Timestamp, np.datetime64)):
        # if a scalar date value, then convert to pandas to be converted to decimal year
        return timestamp_to_decimal_year(pd.to_datetime(date))
    elif isinstance(date, (pd.Series, mpd.Series, np.ndarray)):
        if date.dtype in [float, int]:
            # if it is already an array of numerical values, then just return it
            return date

    return timestamp_to_decimal_year(pd.to_datetime(convert_date(date)))
