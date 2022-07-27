import filecmp
import tempfile
from ausdex import viz
import shutil


def test_inflation_graph():
    fig = viz.plot_inflation_timeseries("01-01-2019", start_date="06-06-1949", end_date=2020)
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        fig.write_json(tmp.name)

        assert filecmp.cmp(
            "tests/testdata/ausdex/test_inflation_fig.json",
            tmp.name,
        )


def test_cpi_graph():
    fig = viz.plot_cpi_timeseries(start_date="06-06-1949", end_date=2020)
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        fig.write_json(tmp.name)
        assert filecmp.cmp(
            "tests/testdata/ausdex/test_cpi_fig.json",
            tmp.name,
        )


def test_plot_cpi_change():
    fig = viz.plot_cpi_change(start_date="1990", end_date="2022")
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        fig.write_json(tmp.name)
        expected = "tests/testdata/ausdex/test_plot_cpi_change.json"
        # shutil.copy(tmp.name, expected)
        assert filecmp.cmp(
            expected,
            tmp.name,
        )
