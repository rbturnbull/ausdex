import unittest
from unittest.mock import patch
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import modin.pandas as mpd
import modin.config as cfg

cfg.IsDebug.put(True)

from ausdex.dates import convert_date, date_time_to_decimal_year


class TestDates(unittest.TestCase):
    def test_str(self):
        result = convert_date("2006")
        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_equal(result, np.array("2006-01-01", dtype="datetime64[D]"))

    def test_int(self):
        np.testing.assert_equal(convert_date(2006), np.array("2006-01-01", dtype="datetime64[D]"))

    def test_float(self):
        np.testing.assert_equal(convert_date(2006.5), np.array("2006-07-02", dtype="datetime64[D]"))

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


class TestDateToDecimalYear(unittest.TestCase):
    def test_int(self):
        result = date_time_to_decimal_year(1995)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result, 1995)

    def test_float(self):
        result = date_time_to_decimal_year(1995.5)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result, 1995.5)

    def test_float_list(self):
        result = date_time_to_decimal_year([1995.5])
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result, 1995.5)

    def test_datetime(self):
        result = date_time_to_decimal_year(datetime(1996, 7, 2))
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result, 1996.5)

    def test_float_tuple(self):
        result = date_time_to_decimal_year((1995.5, 1996.6))
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result[0], 1995.5)
        self.assertEqual(result[1], 1996.6)

    def test_float_array(self):
        result = date_time_to_decimal_year(np.array([1995.5, 1996.6]))
        self.assertIsInstance(result, np.ndarray)
        self.assertTrue(all([x == y for x, y in zip(result, [1995.5, 1996.6])]))

    def test_int_array(self):
        result = date_time_to_decimal_year(np.array([1995, 1996]))
        self.assertIsInstance(result, np.ndarray)
        self.assertTrue(all([x == y for x, y in zip(result, [1995, 1996])]))

    def test_datetime_array(self):
        result = date_time_to_decimal_year(np.array([np.datetime64("1995-01-01"), np.datetime64("1996-07-02")]))
        self.assertIsInstance(result, np.ndarray)
        # trues = [x == y for x, y in zip(result, [1995.5, 1996.6])]
        self.assertAlmostEqual(result[0], 1995.0, 4)
        self.assertEqual(result[1], 1996.5)

    def test_str_array(self):
        result = date_time_to_decimal_year(np.array(["1995-01-01", "1996-07-02"]))
        self.assertIsInstance(result, np.ndarray)
        # trues = [x == y for x, y in zip(result, [1995.5, 1996.6])]
        self.assertAlmostEqual(result[0], 1995.0, 4)
        self.assertEqual(result[1], 1996.5)

    def test_str_series(self):
        result = date_time_to_decimal_year(pd.Series(np.array(["1995-01-01", "1996-07-02"])))
        self.assertIsInstance(result, np.ndarray)
        # trues = [x == y for x, y in zip(result, [1995.5, 1996.6])]
        self.assertAlmostEqual(result[0], 1995.0, 4)
        self.assertEqual(result[1], 1996.5)

    def test_datetime_series(self):
        result = date_time_to_decimal_year(
            pd.Series(np.array([np.datetime64("1995-01-01"), np.datetime64("1996-07-02")]))
        )
        self.assertIsInstance(result, np.ndarray)
        # trues = [x == y for x, y in zip(result, [1995.5, 1996.6])]
        self.assertAlmostEqual(result[0], 1995.0, 4)
        self.assertEqual(result[1], 1996.5)

    def test_datetime_mpdseries(self):
        result = date_time_to_decimal_year(
            mpd.Series(np.array([np.datetime64("1995-01-01"), np.datetime64("1996-07-02")]))
        )
        self.assertIsInstance(result, np.ndarray)
        # trues = [x == y for x, y in zip(result, [1995.5, 1996.6])]
        self.assertAlmostEqual(result[0], 1995.0, 4)
        self.assertEqual(result[1], 1996.5)

    def test_str_mpdseries(self):
        result = date_time_to_decimal_year(mpd.Series(np.array(["1995-01-01", "1996-07-02"])))
        self.assertIsInstance(result, np.ndarray)
        # trues = [x == y for x, y in zip(result, [1995.5, 1996.6])]
        self.assertAlmostEqual(result[0], 1995.0, 4)
        self.assertEqual(result[1], 1996.5)
