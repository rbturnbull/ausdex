import unittest
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
from appdirs import user_cache_dir
import geopandas as gpd
from aucpi.seifa_vic.data_wrangling import preprocess_victorian_datasets
import pandas as pd

MOCKED_FILES = ['seifa_1986_aurin.geojson', 'seifa_1991_aurin.geojson',"state_suburb_codes_2011..csv.zip",
                 'seifa_1996_aurin.geojson', 'seifa_2001_aurin.geojson', 'seifa_2006.geojson',
                 'victoria_councils','victoria_suburbs', 'seifa_2006_cd.xls', 'seifa_suburb_2011.xls',
                  'seifa_suburb_2016.xls', 'mock_completed.csv' ]

def mock_user_get_cached_path(filename):
    print(f'using cached test data for {filename}')
    if filename in MOCKED_FILES:
        if filename == "state_suburb_codes_2011..csv.zip":
            return Path(__file__).parent.resolve() / "testdata" / 'aucpi'/'mock_gis'/'SSC_2011_AUST.csv'
        else:
            return Path(__file__).parent.resolve() / "testdata" / 'aucpi'/'mock_gis'/filename
    else:
        cache_dir = Path(user_cache_dir("aucpi"))
        cache_dir.mkdir(exist_ok=True, parents=True)
        return cache_dir / filename

def mock_load_shapefile_data(filename):
    if filename == 'seifa_2006_cd_shapefile':
        return gpd.read_file(mock_user_get_cached_path('seifa_2006.geojson'))

def mock_preproces_vic_datasets(force_rebuild=False, save_file=False):
    print('loading mocked completed dataset')
    return pd.read_csv(mock_user_get_cached_path('mock_completed.csv'))

class TestSeifaVicSetup(unittest.TestCase):
    @patch("aucpi.seifa_vic.data_io.get_cached_path", lambda filename: mock_user_get_cached_path(filename))
    @patch("aucpi.seifa_vic.data_io.load_shapefile_data", lambda filename: mock_load_shapefile_data(filename))
    def test_preprocess_victorian_datasets(self):
        df = preprocess_victorian_datasets(force_rebuild=True, save_file=False)

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
        self.assertIn("ASCOT - BALLARAT",df.Site_suburb.unique())

    @patch('aucpi.seifa_vic.seifa_vic.preprocess_victorian_datasets', lambda force_rebuild: mock_preproces_vic_datasets(False))
    def test_seifa_interpolation(self):
        from aucpi.seifa_vic.seifa_vic import interpolate_vic_suburb_seifa

        with self.subTest(msg="null test"):
            value = interpolate_vic_suburb_seifa(
                [1980, 1987], "ABBOTSFORD", "ier_score",
            )
            # self.assertTrue(value[0] == np.nan)
            # print(value)
            self.assertTrue(np.isnan(value[0]))
            self.assertAlmostEqual(value[1], 955.5048835511469, places=3)

        with self.subTest(msg="extrapolate test"):
            value = interpolate_vic_suburb_seifa(
                [1980, 2000], "ABBOTSFORD", "ier_score", fill_value = 'extrapolate'
            )
            self.assertAlmostEqual(value[0], 868.1914314671592, places=3)
            self.assertAlmostEqual(value[1], 1055.278795, places=3)
        with self.subTest(msg="boundary_value_test"):
            value = interpolate_vic_suburb_seifa(
                [1980, 1986], "ABBOTSFORD", "ieo_score", fill_value="boundary_value"
            )
            self.assertAlmostEqual(value[0], value[1], places=3)

        # print(value)
