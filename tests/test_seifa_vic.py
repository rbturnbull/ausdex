import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from aucpi.seifa_vic.data_wrangling import preprocess_victorian_datasets


def mock_user_cache_dir(filename):
    return Path(__file__).parent.resolve() / "testdata" / filename


class TestSeifaVicSetup(unittest.TestCase):
    @patch("aucpi.files.user_cache_dir", lambda filename: mock_user_cache_dir(filename))
    def test_preprocess_victorian_datasets(self):
        df = preprocess_victorian_datasets(force_rebuild=True)

        cols = [
            "ieo_score",
            "ier_score",
            "irsad_score",
            "rirsa_score",
            "uirsa_score",
            "irsd_score",
            "year",
            "Site_suburb",
        ]
        for col in cols:
            assert col in df.columns, f"{col} not in dataset"
        self.assertEqual(df.year.max(), 2016)
        self.assertEqual(df.year.min(), 1986)


class TestSeifaVicInterpolation(unittest.TestCase):
    def test_seifa_interpolation(self):
        from aucpi.seifa_vic.seifa_vic import interpolate_vic_suburb_seifa

        with self.subTest(msg="extrapolate test"):
            value = interpolate_vic_suburb_seifa(
                [1980, 1987], "ABBOTSFORD", "ier_score"
            )
            self.assertAlmostEqual(value[0], 868.191431, places=3)
            self.assertAlmostEqual(value[1], 955.5048835511469, places=3)
        with self.subTest(msg="boundary_value_test"):
            value = interpolate_vic_suburb_seifa(
                [1980, 1986], "ABBOTSFORD", "ieo_score", fill_value="boundary_value"
            )
            self.assertAlmostEqual(value[0], value[1], places=3)

        print(value)
