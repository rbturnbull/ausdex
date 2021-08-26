from datetime import datetime
import unittest
import numpy as np
import pandas as pd

from aucpi import adjust, Aucpi

class TestAucpi(unittest.TestCase):
    """ 
    Tests the aucpi adjust function.
    
    Gold values taken from https://www.rba.gov.au/calculator/quarterDecimal.html
    """
    def test_scalar(self):
        value = adjust(13, "March 1991", evaluation_date="June 2010")
        self.assertAlmostEqual( value, 21.14, delta=0.01 )

    def test_scalar_datetime(self):
        value = adjust(1432, datetime(1990, 9, 1), evaluation_date=datetime(2003, 12, 1))
        self.assertAlmostEqual( value, 1_979.90, delta=0.01 )

    def test_scalar_negative(self):
        value = adjust(-1432, datetime(1990, 9, 1), evaluation_date=datetime(2003, 12, 1))
        self.assertAlmostEqual( value, -1_979.90, delta=0.01 )

    def test_scalar_early(self):
        value = adjust(1, datetime(1900, 9, 1))
        self.assertTrue( np.isnan(value) )

    def test_no_evaluation_date(self):
        value = adjust(42, "Sep 1990")
        self.assertGreaterEqual( value, 80 ) # This will fail if there is significant deflation after 2021

    def test_numpy(self):
        array = np.array([30, 52.35, -63])
        value = adjust(array, "June 1981", evaluation_date="Feb 2011")
        np.testing.assert_allclose( value, np.array([102.36, 178.62, -214.95]), atol=1e-02)

    def test_cpi_australia_at_pandas(self):
        dates = pd.to_datetime(pd.Series(["June 1 2019", "February 3 1944", "Feb 3 1997"]))
        aucpi = Aucpi()
        results = aucpi.cpi_australia_at( dates )
        np.testing.assert_allclose( results, np.array([114.8, np.nan, 67]), atol=1e-02)

    def test_pandas(self):
        df = pd.DataFrame(data=[
            ["June 1975", 56],
            ["Feb 1976", 56],
            ["4 October 1977", -60],
        ], columns=["date", "value"])
        results = adjust(df.value, df.date, evaluation_date="5 April 2005")
        self.assertEqual( results.size, len(df) )

        np.testing.assert_allclose( results, np.array([290.99, 273.67, -240.29]), atol=1e-02)

    def test_pandas_evaluation_dates(self):
        df = pd.DataFrame(data=[
            ["Dec 1990", "Sep 1970", 34.86, 5.79],
            ["Sep 1970", "Dec 1990", 5.79, 34.86],
            ["5 April 2005", "4 October 1977", -240.29, -60],
        ], columns=["date", "evaluation", "value", "gold"])
        results = adjust(df.value, df.date, evaluation_date=df.evaluation)
        self.assertEqual( results.size, len(df) )

        np.testing.assert_allclose( results, df.gold, atol=1e-02)

    def test_get_abs_by_date(self):
        aucpi = Aucpi()
        file = aucpi.get_abs_by_date( "640101", datetime(2021,8,26) )
        self.assertIn("640101-jun-2021.xls", str(file))