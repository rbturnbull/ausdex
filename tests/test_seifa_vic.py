import unittest
import numpy as np
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from appdirs import user_cache_dir
import geopandas as gpd
from ausdex.seifa_vic.data_wrangling import preprocess_victorian_datasets
import pandas as pd
from typer.testing import CliRunner
from ausdex import main
from ausdex.seifa_vic.data_io import make_aurin_config, load_aurin_data
from ausdex.files import get_cached_path
import json
import datetime

MOCKED_FILES = [
    "seifa_1986_aurin.geojson",
    "seifa_1991_aurin.geojson",
    "state_suburb_codes_2011..csv.zip",
    "seifa_1996_aurin.geojson",
    "seifa_2001_aurin.geojson",
    "seifa_2006.geojson",
    "victoria_councils",
    "victoria_suburbs",
    "seifa_2006_cd.xls",
    "seifa_suburb_2011.xls",
    "seifa_suburb_2016.xls",
    "mock_completed.csv",
    "aurin_schemas.json",
]


def mock_user_get_cached_path(filename):
    print(f"using cached test data for {filename}")
    if filename in MOCKED_FILES:
        if filename == "state_suburb_codes_2011..csv.zip":
            return (
                Path(__file__).parent.resolve()
                / "testdata"
                / "ausdex"
                / "mock_gis"
                / "SSC_2011_AUST.csv"
            )
        else:
            return (
                Path(__file__).parent.resolve()
                / "testdata"
                / "ausdex"
                / "mock_gis"
                / filename
            )
    else:
        cache_dir = Path(user_cache_dir("ausdex"))
        cache_dir.mkdir(exist_ok=True, parents=True)
        return cache_dir / filename


def mock_load_shapefile_data(filename):
    if filename == "seifa_2006_cd_shapefile":
        return gpd.read_file(mock_user_get_cached_path("seifa_2006.geojson"))


def mock_preproces_vic_datasets(force_rebuild=False, save_file=False):
    print("loading mocked completed dataset")
    return pd.read_csv(mock_user_get_cached_path("mock_completed.csv"))


class TestSeifaVicSetup(unittest.TestCase):
    @patch(
        "ausdex.seifa_vic.data_io.get_cached_path",
        lambda filename: mock_user_get_cached_path(filename),
    )
    @patch(
        "ausdex.seifa_vic.data_wrangling.load_shapefile_data",
        lambda filename: mock_load_shapefile_data(filename),
    )
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
        self.assertIn("ASCOT - BALLARAT", df.Site_suburb.unique())
        self.assertNotIn("ASCOT - BALLARAT CITY", df.Site_suburb.unique())


@patch(
    "ausdex.seifa_vic.seifa_vic.preprocess_victorian_datasets",
    lambda force_rebuild: mock_preproces_vic_datasets(False),
)
class TestSeifaInterpolation(unittest.TestCase):
    def setUp(self) -> None:
        from ausdex.seifa_vic.seifa_vic import interpolate_vic_suburb_seifa

        self.interpolate = interpolate_vic_suburb_seifa
        return super().setUp()

    def test_interpolation_null(self):
        value = self.interpolate(
            [1980, 1987],
            "ABBOTSFORD",
            "ier_score",
        )
        # self.assertTrue(value[0] == np.nan)
        # print(value)
        self.assertTrue(np.isnan(value[0]))
        self.assertAlmostEqual(value[1], 955.5048835511469, places=3)

    def test_interpolation_extrapolate(self):
        value = self.interpolate(
            pd.Series([1980, 2000]),
            "ABBOTSFORD",
            "ier_score",
            fill_value="extrapolate",
        )
        self.assertAlmostEqual(value[0], 868.1914314671592, places=3)
        self.assertAlmostEqual(value[1], 1055.278795, places=3)

    def test_interpolate_boundary_value(self):
        value = self.interpolate(
            np.array([1980, 1986]),
            "ABBOTSFORD",
            "ieo_score",
            fill_value="boundary_value",
        )
        self.assertAlmostEqual(value[0], value[1], places=3)

    def test_interpolate_multiple_suburbs(self):
        value = self.interpolate(
            ["1-7-1980", "31-10-1986"],
            pd.Series(["kew", "ABBOTSFORD"]),
            "ieo_score",
            fill_value="boundary_value",
        )
        self.assertAlmostEqual(value[0], 1179.648871, places=3)
        self.assertAlmostEqual(994.3434, value[1], places=3)

    def test_interpolate_multiple_suburbs_array(self):
        value = self.interpolate(
            pd.Series(["1-7-1980", "31-10-1986"]),
            pd.Series(["kew", "ABBOTSFORD"]).values,
            "ieo_score",
            fill_value="boundary_value",
        )
        self.assertAlmostEqual(value[0], 1179.648871, places=3)
        self.assertAlmostEqual(994.3434, value[1], places=3)

    def test_interpolate_list_datetimes_datetimes(self):
        value = self.interpolate(
            pd.Series([datetime.datetime(1980, 7, 1), datetime.datetime(1986, 10, 31)]),
            pd.Series(["kew", "ABBOTSFORD"]).values,
            "ieo_score",
            fill_value="boundary_value",
        )
        self.assertAlmostEqual(value[0], 1179.648871, places=3)
        self.assertAlmostEqual(994.3434, value[1], places=3)

    def test_interpolate_single_datetime(self):
        value = self.interpolate(
            datetime.datetime(1986, 10, 31),
            "kew",
            "ieo_score",
            fill_value="boundary_value",
        )
        self.assertAlmostEqual(value, 1179.9308, places=3)
        # self.assertAlmostEqual(1013.1802726224083, value[1], places=3)

    def test_seifa_vic_cli(self):
        runner = CliRunner()
        result = runner.invoke(
            main.app, ["seifa-vic", "1991", "abbotsford", "ier_score"]
        )
        assert result.exit_code == 0
        assert "1005.03" in result.stdout


def patch_get_cached_path_schema(file) -> Path:
    new_filename = "schema_" + file
    local_path = get_cached_path(new_filename)
    if local_path.exists() == True:
        local_path.unlink()
    return local_path


def patch_download_from_aurin(wfs_aurin, dataset, links, local_path):
    print("patching aurin download for schema")
    schema = wfs_aurin.get_schema(links[dataset])
    with open(local_path, "w") as file:
        json.dump(schema, file)


def patch_open_geopandas(file):
    print("patching open geopandas")
    with open(file, "r") as f:
        out = json.load(f)
    return out


def load_aurin_schema():
    fname = mock_user_get_cached_path("aurin_schemas.json")
    with open(fname, "r") as f:
        out = json.load(f)
    return out


class TestDataIO(unittest.TestCase):
    def setUp(self) -> None:
        aurin_creds = get_cached_path("aurin_creds.json")
        if aurin_creds.exists() == True:
            aurin_creds.unlink()
        return super().setUp()

    @patch("ausdex.seifa_vic.data_io._get_input", lambda msg: "test_username")
    @patch("ausdex.seifa_vic.data_io._get_getpass", lambda msg: "test_password")
    @patch("ausdex.seifa_vic.data_io.get_config_ini", Path("does not exist"))
    def test_make_aurin_config_as_json(self):
        make_aurin_config()
        with open(get_cached_path("aurin_creds.json"), "r") as file:
            creds = json.load(file)
        self.assertEqual(creds["username"], "test_username")
        self.assertEqual(creds["password"], "test_password")

    @patch(
        "ausdex.seifa_vic.data_io.download_from_aurin",
        lambda wfs_aurin, dataset, links, local_path: patch_download_from_aurin(
            wfs_aurin, dataset, links, local_path
        ),
    )
    @patch(
        "ausdex.seifa_vic.data_io.open_geopandas",
        lambda file: patch_open_geopandas(file),
    )
    @patch(
        "ausdex.seifa_vic.data_io.get_cached_path",
        lambda filename: patch_get_cached_path_schema(filename),
    )
    def test_aurin_downloads(self):
        datasets = [
            "seifa_2001_aurin",
            "seifa_1996_aurin",
            "seifa_1991_aurin",
            "seifa_1986_aurin",
        ]
        saved_schema = load_aurin_schema()
        data = load_aurin_data(datasets)

        for d, dset in zip(data, datasets):
            self.assertDictEqual(saved_schema[dset], d)
