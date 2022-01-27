import unittest
import numpy as np
import os
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from appdirs import user_cache_dir
import geopandas as gpd
import warnings
import shutil
from ausdex.seifa_vic.data_wrangling import preprocess_victorian_datasets
from ausdex.seifa_vic.seifa_vic import Metric
import pandas as pd
from typer.testing import CliRunner
from ausdex import main
from ausdex.seifa_vic.data_io import (
    get_data_links,
    load_aurin_config,
    load_aurin_data,
    download_from_aurin,
    get_aurin_wfs,
    load_shapefile_data,
    load_victorian_suburbs_metadata,
)
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
    "victoria_councils.geojson",
    "victoria_suburbs.geojson",
    "seifa_2006_cd.xls",
    "seifa_suburb_2011.xls",
    "seifa_suburb_2016.xls",
    "mock_completed.csv",
    "aurin_schemas.json",
    "seifa_2011_sa1.xls",
    "seifa_2016_sa1.xls",
    "sa1_gis_2011.geojson",
    "sa1_gis_2016.geojson",
]


def fake_data_cached_path(filename):
    return (
        Path(__file__).parent.resolve() / "testdata" / "ausdex" / "mock_gis" / filename
    )


def mock_user_get_cached_path(filename):
    print(f"using cached test data for {filename}")
    if filename in MOCKED_FILES:
        if filename == "state_suburb_codes_2011..csv.zip":
            fcp = fake_data_cached_path("SSC_2011_AUST.csv")
            print(f"loading test file from {fcp}")
            return fcp

        else:
            fcp = fake_data_cached_path(filename)
            print(f"loading test file from {fcp}")
            return fcp

    else:
        cache_dir = Path(user_cache_dir("ausdex"))
        cache_dir.mkdir(exist_ok=True, parents=True)
        return cache_dir / filename


def mock_load_shapefile_data(filename):
    if filename == "seifa_2006_cd_shapefile":
        return gpd.read_file(mock_user_get_cached_path("seifa_2006.geojson"))
    elif filename == "sa1_gis_2011":
        return gpd.read_file(mock_user_get_cached_path("sa1_gis_2011.geojson"))
    elif filename == "sa1_gis_2016":
        return gpd.read_file(mock_user_get_cached_path("sa1_gis_2016.geojson"))


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

    def test_group_repeat_names_vic(self):
        from ausdex.seifa_vic.data_wrangling import group_repeat_names_vic

        ids = [
            "VIC2961",
            "VIC2967",
            "VIC2976",
            "VIC2984",
            "VIC2990",
            "VIC2969",
            "VIC2963",
        ]
        fixed_suburbs = [
            "BELLFIELD - GRAMPIANS",
            "BELLFIELD - BANYULE",
            "HAPPY VALLEY - SWAN HILL",
            "HILLSIDE - MELTON",
            "REEDY CREEK - MITCHELL",
            "SPRINGFIELD - MACEDON RANGES",
            "STONY CREEK - HEPBURN",
        ]
        for id, suburb in zip(ids, fixed_suburbs):
            x = {"loc_pid": id, "suburb_name_combined": "test_failed"}
            value = group_repeat_names_vic(x)
            self.assertAlmostEqual(value, suburb)
        x = {"loc_pid": "wrong", "suburb_name_combined": "test_failed"}
        value = group_repeat_names_vic(x)
        self.assertEqual(value, "test_failed")

    @patch(
        "ausdex.seifa_vic.seifa_vic.preprocess_victorian_datasets",
        lambda force_rebuild: mock_preproces_vic_datasets(False)
        if force_rebuild == True
        else None,
    )
    def test_assemble_data_cli(self):
        runner = CliRunner()
        result = runner.invoke(main.app, ["seifa-vic-assemble"])

        assert result.exit_code == 0
        assert "Data loaded" in result.stdout


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

    def test_suburb_guess_misspelt(self):
        value = self.interpolate(
            [1980, 1987],
            "ABBOTSFORDXX",
            "ier_score",
            guess_misspelt=True,
        )
        self.assertTrue(np.isnan(value[0]))
        self.assertAlmostEqual(value[1], 955.5048835511469, places=3)

    def test_interpolation_negative(self):
        value = self.interpolate(
            2200, "ASCOT - BALLARAT", Metric["ier_score"], fill_value="extrapolate"
        )
        # self.assertTrue(value[0] == np.nan)
        # print(value)
        self.assertTrue(value == 0)

    def test_interpolation_onevalue(self):
        from ausdex.seifa_vic import SeifaVic

        seifa_vic = SeifaVic(False)
        seifa_vic.df = pd.DataFrame(
            {
                "Site_suburb": ["TEST_SUB1", "test_sub2"],
                "ier_score": [36.4, 38.5],
                "year": [2000, 2011],
            }
        )
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            out = seifa_vic.get_seifa_interpolation(
                2011, "TEST_SUB1", "ier_score", fill_value="extrapolate"
            )
            self.assertEqual(36.4, out)
            assert len(w) == 1
            assert (
                "Suburb 'TEST_SUB1' only has one value for ier_score, assuming flat line"
                in str(w[-1].message)
            )

    def test_interpolation_novalue(self):
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            value = self.interpolate(
                2200, "Fake", "ier_score", fill_value="extrapolate"
            )
            # self.assertTrue(value[0] == np.nan)
            # print(value)
            self.assertTrue(np.isnan(value))
            assert len(w) == 1
            assert "No suburb named 'FAKE'. Returning NaN." in str(w[-1].message)

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

    def test_interpolate_lga(self):
        value = self.interpolate(
            datetime.datetime(1996, 10, 31),
            "ASCOT",
            "ieo_score",
            lga="Greater Bendigo",
        )
        self.assertAlmostEqual(value, 973.18854015, places=3)
        # self.assertAlmostEqual(1013.1802726224083, value[1], places=3

    def test_interpolate_lga_list(self):
        value = self.interpolate(
            [datetime.datetime(1996, 10, 31), datetime.datetime(1986, 10, 31)],
            ["ASCOT", "kew"],
            "ieo_score",
            lga=["Greater Bendigo", "Boroondara"],
        )
        self.assertAlmostEqual(value[0], 973.18854015, places=3)
        self.assertAlmostEqual(value[1], 1179.9308, places=3)

    def test_interpolate_lga_series(self):
        value = self.interpolate(
            pd.Series(
                [datetime.datetime(1996, 10, 31), datetime.datetime(1986, 10, 31)]
            ),
            pd.Series(["ASCOT", "kew"]),
            "ieo_score",
            lga=pd.Series(["Greater Bendigo", "Boroondara"]),
        )
        self.assertAlmostEqual(value[0], 973.18854015, places=3)
        self.assertAlmostEqual(value[1], 1179.9308, places=3)

    def test_seifa_vic_cli(self):
        runner = CliRunner()
        result = runner.invoke(
            main.app, ["seifa-vic", "1991", "abbotsford", "ier_score"]
        )
        assert result.exit_code == 0
        assert "1005.03" in result.stdout

    def test_seifa_vic_cli_lga(self):
        runner = CliRunner()
        result = runner.invoke(
            main.app,
            [
                "seifa-vic",
                "1996-10-31",
                "ascot",
                "ieo_score",
                "--lga",
                "Greater Bendigo",
            ],
        )
        assert result.exit_code == 0
        assert "973.19" in result.stdout

    def test_get_repeated_names(self):
        from ausdex.seifa_vic.seifa_vic import get_repeated_names

        names = get_repeated_names()
        assert "ASCOT - BALLARAT" in names


def patch_get_cached_path_schema(file) -> Path:
    new_filename = "schema_" + file
    local_path = Path(__file__).parent / "testdata" / "tmp" / new_filename
    if local_path.exists() == True:
        local_path.unlink()
    return local_path


def patch_download_from_aurin(wfs_aurin, dataset, links, local_path):
    print("patching aurin download for schema")
    schema = wfs_aurin.get_schema(links[dataset])
    Path(local_path).parent.mkdir(exist_ok=True)
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


def patch_unzip(local_path, new_path_name):
    new_path_name.mkdir(exist_ok=True, parents=True)
    (new_path_name / "shapefile.shp").touch()
    (new_path_name / "shapefile.shx").touch()


def patch_open_geopandas_2(filename):
    return filename


@patch(
    "ausdex.seifa_vic.data_io.get_aurin_creds_path",
    lambda: Path(__file__).parent / "aurin_creds_dummy.json",
)
class TestDataIO(unittest.TestCase):
    def setUp(self) -> None:

        aurin_creds = Path(__file__).parent / "aurin_creds_dummy.json"
        self.aurin_dummy_creds = aurin_creds
        print(aurin_creds)
        if aurin_creds.exists() == True:
            aurin_creds.unlink()
        aurin_creds.parent.mkdir(exist_ok=True, parents=True)
        return super().setUp()

    def tearDown(self) -> None:
        if self.aurin_dummy_creds.exists() == True:
            os.remove(self.aurin_dummy_creds)
        if (Path(__file__).parent / "testdata" / "tmp").exists() == True:
            shutil.rmtree((Path(__file__).parent / "testdata" / "tmp"))
        return super().tearDown()

    @patch("ausdex.seifa_vic.data_io._get_input", lambda msg: "test_username")
    @patch("ausdex.seifa_vic.data_io._get_getpass", lambda msg: "test_password")
    @patch("ausdex.seifa_vic.data_io.get_config_ini", lambda: Path("does not exist"))
    def test_make_aurin_config_as_json(self):
        from ausdex.seifa_vic.data_io import get_aurin_creds_path

        load_aurin_config()
        with open(get_aurin_creds_path(), "r") as file:
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
    def test_aurin_data(self):
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

    @patch(
        "ausdex.seifa_vic.data_io.get_cached_path",
        lambda filename: mock_user_get_cached_path(filename),
    )
    def test_aurin_already_downloaded(self):
        gdf = load_aurin_data("seifa_2001_aurin")
        self.assertIn("geometry", gdf[0].columns)

    def test_aurin_download(self):
        wfs = get_aurin_wfs()
        links = get_data_links()
        test_aurin_dl = get_cached_path("test_aurin_dl.geojson")
        download_from_aurin(
            wfs,
            "seifa_2001_aurin",
            links,
            test_aurin_dl,
            bbox=(125, -42.01, 125.01, -42.0),
        )

    def test_load_victorian_suburbs_metadata(self):
        df = load_victorian_suburbs_metadata()
        self.assertIn("locality_pid", df.columns)
        self.assertIn("locality_name", df.columns)

    @patch(
        "ausdex.seifa_vic.data_io.open_geopandas",
        lambda file: patch_open_geopandas_2(file),
    )
    @patch(
        "ausdex.seifa_vic.data_io.unzip",
        lambda local_path, new_path_name: patch_unzip(local_path, new_path_name),
    )
    @patch("ausdex.seifa_vic.data_io.cached_download", lambda url, local_path: None)
    @patch(
        "ausdex.seifa_vic.data_io.get_data_links",
        lambda: {"test_dataset": "test_dataset_folder"},
    )
    def test_load_shapefile_data(self):
        out_file = load_shapefile_data("test_dataset")
        print(out_file)
        self.assertIn("shp", out_file.name)
        self.assertIn("unzipped", out_file.parent.name)
        shutil.rmtree(out_file.parent)


@patch(
    "ausdex.seifa_vic.data_io.get_cached_path",
    lambda filename: mock_user_get_cached_path(filename),
)
@patch(
    "ausdex.seifa_vic.data_wrangling.load_shapefile_data",
    lambda filename: mock_load_shapefile_data(filename),
)
@patch(
    "ausdex.seifa_vic.seifa_vic.preprocess_victorian_datasets",
    lambda force_rebuild: mock_preproces_vic_datasets(False),
)
class TestSeifaGisViz(unittest.TestCase):
    def setUp(self) -> None:
        from ausdex import seifa_vic

        self.seifa_vic = seifa_vic
        self.tmp = Path("tmp")
        self.tmp.mkdir(exist_ok=True)
        return super().setUp()

    def tearDown(self) -> None:

        shutil.rmtree(self.tmp)
        return super().tearDown()

    def test_seifa_gis(self):
        from ausdex.seifa_vic import get_seifa_gis

        gdf = get_seifa_gis("05-11-2015", "ier_score", fill_value="extrapolate")
        print(gdf.shape)
        self.assertEqual(type(gdf), gpd.GeoDataFrame)
        self.assertIn("Site_suburb", gdf.columns)
        self.assertIn("ier_score", gdf.columns)

    def test_seifa_map(self):
        from ausdex.seifa_vic import get_seifa_map

        fig = get_seifa_map(
            "05-11-2015", Metric["ier_score"], fill_value="extrapolate", simplify=0.001
        )
        # fig.write_json('tests/testdata/ausdex/mock_gis/test_map.json')
        fig.write_json(self.tmp / "test_map.json")
        import filecmp

        self.assertTrue(
            filecmp.cmp(
                "tests/testdata/ausdex/mock_gis/test_map.json",
                self.tmp / "test_map.json",
            )
        )

    def test_seifa_plot(self):
        from ausdex.seifa_vic import create_timeseries_chart

        fig = create_timeseries_chart(
            ["abbotsford", "ASCOT - BALLARAT"], Metric["irsd_score"]
        )
        # fig.write_json('tests/testdata/ausdex/mock_gis/test_fig.json')
        fig.write_json(self.tmp / "test_fig.json")

        import filecmp

        self.assertTrue(
            filecmp.cmp(
                "tests/testdata/ausdex/mock_gis/test_fig.json",
                self.tmp / "test_fig.json",
            )
        )

    def test_seifa_vic_gis_cli(self):
        runner = CliRunner()
        result = runner.invoke(
            main.app,
            [
                "seifa-vic-gis",
                "05-11-2015",
                "ier_score",
                str(self.tmp / "tmp_gis.geojson"),
            ],
        )
        assert result.exit_code == 0
        gdf = gpd.read_file(self.tmp / "tmp_gis.geojson")
        self.assertEqual(type(gdf), gpd.GeoDataFrame)
        self.assertIn("Site_suburb", gdf.columns)
        self.assertIn("ier_score", gdf.columns)

    def test_seifa_vic_map_cli(self):
        runner = CliRunner()
        result = runner.invoke(
            main.app,
            [
                "seifa-vic-map",
                "05-11-2015",
                "ier_score",
                str(self.tmp / "test_map.html"),
                "--fill-value",
                "extrapolate",
                "--min-y",
                "-37.5",
            ],
        )
        assert result.exit_code == 0
        assert (self.tmp / "test_map.html").exists()

    def test_seifa_vic_plot_cli(self):
        runner = CliRunner()
        result = runner.invoke(
            main.app,
            [
                "seifa-vic-plot",
                "ier_score",
                str(self.tmp / "test_plot.html"),
                "abbotsford",
                "ASCOT - BALLARAT",
            ],
        )
        assert result.exit_code == 0
        assert (self.tmp / "test_plot.html").exists()

    def test_gis_clipping(self):
        from ausdex.gis_utils import clip_gdf
        from ausdex.seifa_vic import get_seifa_gis

        gdf = get_seifa_gis("05-11-2015", "ier_score", fill_value="extrapolate")

        gdf_clip_one = clip_gdf(gdf, min_y=-37.5)

        self.assertEqual(gdf_clip_one.shape[0], 1)
        self.assertIn("ASCOT", gdf_clip_one.Site_suburb[0])
        from shapely.geometry import Polygon

        clip_gs = gpd.GeoSeries(
            Polygon(
                [
                    [143.805, -37.5],
                    [143.805, -37.575],
                    [143.800, -37.575],
                    [143.800, -37.5],
                ]
            )
        )
        clip_gs.crs = gdf.crs

        gdf_clip_two = clip_gdf(gdf, clip_mask=clip_gs)
        print(gdf_clip_two)
        self.assertEqual(gdf_clip_two.shape[0], 1)
        self.assertIn("ier_score", gdf_clip_two.columns)
        self.assertIn("ALFREDTON", gdf_clip_two.Site_suburb.item())
