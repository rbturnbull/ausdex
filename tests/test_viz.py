import filecmp
import tempfile
import shutil
import pytest


def test_inflation_graph(check_viz):
    fig = check_viz.plot_inflation_timeseries("01-01-2019", start_date="06-06-1949", end_date=2020)
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        fig.write_json(tmp.name)
        expected = "tests/testdata/ausdex/test_inflation_fig.json"
        # shutil.copy(tmp.name, expected) # hack to copy the file to the expected location
        if not filecmp.cmp(expected, tmp.name):
            raise ValueError("test_inflation_fig.json not the same as expected")


def test_cpi_graph(check_viz):
    fig = check_viz.plot_cpi_timeseries(start_date="06-06-1949", end_date=2020)
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        fig.write_json(tmp.name)
        expected = "tests/testdata/ausdex/test_cpi_fig.json"
        # shutil.copy(tmp.name, expected) # hack to copy the file to the expected location
        if not filecmp.cmp(expected, tmp.name):
          raise ValueError("test_cpi_fig.json not the same as expected")


def test_plot_cpi_change(check_viz):
    fig = check_viz.plot_cpi_change(start_date="1990", end_date="2022")
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        fig.write_json(tmp.name)
        expected = "tests/testdata/ausdex/test_plot_cpi_change.json"
        # shutil.copy(tmp.name, expected) # hack to copy the file to the expected location
        if not filecmp.cmp(expected, tmp.name):
            raise ValueError("test_plot_cpi_change.json not the same as expected")
