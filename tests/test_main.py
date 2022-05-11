import unittest
import re
from unittest.mock import patch

from typer.testing import CliRunner
from plotly.graph_objects import Figure

from ausdex import main


class TestMain(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_version(self):
        result = self.runner.invoke(main.app, ["--version"])
        assert result.exit_code == 0
        assert re.match(r"\d+\.\d+\.\d+", result.stdout)

    @patch("typer.launch")
    def test_repo(self, mock_launch):
        result = self.runner.invoke(main.app, ["repo"])
        assert result.exit_code == 0
        mock_launch.assert_called_once()
        self.assertIn("https://github.com/rbturnbull/ausdex", str(mock_launch.call_args))

    @patch("subprocess.run")
    def test_docs_live(self, mock_subprocess):
        result = self.runner.invoke(main.app, ["docs"])
        assert result.exit_code == 0
        mock_subprocess.assert_called_once()
        self.assertIn("sphinx-autobuild", str(mock_subprocess.call_args))

    @patch("webbrowser.open_new")
    @patch("subprocess.run")
    def test_docs_static(self, mock_subprocess, mock_open_web):
        result = self.runner.invoke(main.app, ["docs", "--no-live"])
        assert result.exit_code == 0
        mock_subprocess.assert_called_once()
        self.assertIn("sphinx-build", str(mock_subprocess.call_args))
        mock_open_web.assert_called_once()

    def test_inflation(self):
        result = self.runner.invoke(
            main.app,
            ["inflation", "13", "March 1991", "--evaluation-date", "June 2010"],
        )
        assert result.exit_code == 0
        assert "21.14" in result.stdout

    def test_inflation_melbourne(self):
        result = self.runner.invoke(
            main.app,
            ["inflation", "13", "March 1991", "--evaluation-date", "May 2022", "--location", "melbourne"],
        )
        assert result.exit_code == 0
        assert "26.95" in result.stdout

    def test_inflation_perth(self):
        result = self.runner.invoke(
            main.app,
            ["inflation", "1", "March 1979", "--location", "Perth", "--evaluation-date", "May 2022"],
        )
        assert result.exit_code == 0
        assert "5.29" in result.stdout

    @patch.object(Figure, "show")
    def test_plot_cpi(self, mock_show):
        result = self.runner.invoke(
            main.app,
            ["plot-cpi"],
        )
        assert result.exit_code == 0
        mock_show.assert_called_once()

    @patch.object(Figure, "show")
    @patch.object(Figure, "write_image")
    def test_plot_cpi_output(self, mock_show, mock_write_image):
        result = self.runner.invoke(
            main.app,
            ["plot-cpi", "--output", "tmp.jpg", "--location", "Melbourne"],
        )
        assert result.exit_code == 0
        mock_show.assert_called_once()
        mock_write_image.assert_called_once()

    @patch.object(Figure, "show")
    def test_plot_inflation(self, mock_show):
        result = self.runner.invoke(
            main.app,
            ["plot-inflation", "2022"],
        )
        assert result.exit_code == 0
        mock_show.assert_called_once()

    @patch.object(Figure, "show")
    @patch.object(Figure, "write_html")
    def test_plot_inflation_output(self, mock_show, mock_write_html):
        result = self.runner.invoke(
            main.app,
            ["plot-inflation", "2022", "--output", "tmp.html", "--location", "Melbourne"],
        )
        assert result.exit_code == 0
        mock_show.assert_called_once()
        mock_write_html.assert_called_once()
