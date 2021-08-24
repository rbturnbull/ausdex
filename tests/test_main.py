import unittest

from typer.testing import CliRunner

from aucpi import main

class TestMain(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_version(self):
        result = self.runner.invoke(main.app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout

    def test_adjust(self):
        result = self.runner.invoke(main.app, ["13", 'March 1991', '--evaluation-date', 'June 2010'])
        assert result.exit_code == 0
        assert "21.14" in result.stdout



