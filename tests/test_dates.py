import unittest
from unittest.mock import patch
from pathlib import Path
from datetime import datetime
import numpy as np

from ausdex.dates import convert_date, date_time_to_decimal_year


class TestDates(unittest.TestCase):
    def test_str(self):
        result = convert_date("2006")
        self.assertIsInstance(result, np.ndarray)
        np.testing.assert_equal(result, np.array("2006-01-01", dtype="datetime64[D]"))

    def test_int(self):
        self.assertEqual(
            convert_date(2006), np.array("2006-01-01", dtype="datetime64[D]")
        )

    def test_float(self):
        self.assertEqual(
            convert_date(2006.5), np.array("2006-07-02", dtype="datetime64[D]")
        )

    # def test_numpy_ints(self):
    #     self.assertEqual( convert_date(2006.5), np.array('2006-07-02', dtype='datetime64[D]') )


class TestDateToDecimalYear(unittest.TestCase):
    def test_int(self):
        result = date_time_to_decimal_year(1995)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result, 1995)

    def test_float(self):
        result = date_time_to_decimal_year(1995.5)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result, 1995.5)

    def test_float_array(self):
        result = date_time_to_decimal_year(np.array([1995.5, 1996.6]))
        self.assertIsInstance(result, np.ndarray)
        self.assertTrue(all([x == y for x, y in zip(result, [1995.5, 1996.6])]))

    def test_int_array(self):
        result = date_time_to_decimal_year(np.array([1995, 1996]))
        self.assertIsInstance(result, np.ndarray)
        self.assertTrue(all([x == y for x, y in zip(result, [1995, 1996])]))

    def test_datetime_array(self):
        result = date_time_to_decimal_year(
            np.array([np.datetime64("1995-1-1"), 1996.6])
        )
        self.assertIsInstance(result, np.ndarray)
        self.assertTrue(all([x == y for x, y in zip(result, [1995.5, 1996.6])]))
