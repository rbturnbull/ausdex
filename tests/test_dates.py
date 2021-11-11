import unittest
from unittest.mock import patch
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import modin.pandas as mpd
import modin.config as cfg

cfg.IsDebug.put(True)

from ausdex.dates import convert_date


class TestDates(unittest.TestCase):
    def test_str(self):
        result = convert_date("2006")
        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_equal(result, np.array("2006-01-01", dtype="datetime64[D]"))

    def test_int(self):
        np.testing.assert_equal(
            convert_date(2006), np.array("2006-01-01", dtype="datetime64[D]")
        )

    def test_float(self):
        np.testing.assert_equal(
            convert_date(2006.5), np.array("2006-07-02", dtype="datetime64[D]")
        )

    def test_datetime(self):
        np.testing.assert_equal(
            convert_date(datetime(2006, 7, 2)),
            np.array("2006-07-02", dtype="datetime64[D]"),
        )

    def test_numpy_ints(self):
        dates = np.array([2006, 2007], dtype=np.int32)
        np.testing.assert_equal(
            convert_date(dates),
            np.array(["2006-01-01", "2007-01-01"], dtype="datetime64[D]"),
        )

    def test_numpy_dates(self):
        dates = np.array(["2006-05-06", "2007-02-04"], dtype="datetime64[D]")
        np.testing.assert_equal(
            convert_date(dates),
            np.array(["2006-05-06", "2007-02-04"], dtype="datetime64[D]"),
        )

    def test_pandas_series(self):
        dates = pd.Series(["Jul 31, 2009", "2010-01-10", datetime(2006, 3, 1)])
        np.testing.assert_equal(
            convert_date(dates),
            np.array(["2009-07-31", "2010-01-10", "2006-03-01"], dtype="datetime64[D]"),
        )

    def test_modin_series(self):
        dates = mpd.Series(["Jul 31, 2009", "2010-01-10", datetime(2006, 3, 1)])
        np.testing.assert_equal(
            convert_date(dates),
            np.array(["2009-07-31", "2010-01-10", "2006-03-01"], dtype="datetime64[D]"),
        )
