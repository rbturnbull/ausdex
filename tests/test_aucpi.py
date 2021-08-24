import unittest
import numpy as np
from datetime import datetime

from aucpi import adjust

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

