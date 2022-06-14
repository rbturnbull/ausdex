from datetime import datetime, timedelta
from io import StringIO
import unittest
from unittest.mock import patch
from pathlib import Path

from ausdex import files


def data_dir():
    return Path(__file__).parent.resolve() / "testdata" / "ausdex"


def urlretrieve_fail():
    raise Exception("failed download")


class TestFiles(unittest.TestCase):
    @patch("urllib.request.urlretrieve")
    def test_cached_download_exists(self, mock_urlretrieve):
        files.cached_download("http://www.example.com", data_dir() / "download.html")
        mock_urlretrieve.assert_not_called()

    @patch("urllib.request.urlretrieve")
    def test_cached_download_empty(self, mock_urlretrieve):
        with self.assertRaises(OSError) as context:
            files.cached_download("http://www.example.com", data_dir() / "empty.html")

    @patch("urllib.request.urlretrieve", urlretrieve_fail)
    def test_cached_download_fail(self):
        with self.assertRaises(files.DownloadError) as context:
            files.cached_download("http://www.example.com", data_dir() / "empty.html")

    def test_cached_download_abs_excel_by_date(self):
        file = files.cached_download_abs_excel_by_date("640101", datetime(2021, 8, 26))
        self.assertIn("640101-jun-2021.xls", str(file))
        file = files.cached_download_abs_excel_by_date("640101", datetime(2020, 1, 12))
        self.assertIn("640101-dec-2019.xls", str(file))

    def test_cached_download_abs_excel_bad_quarter(self):
        with self.assertRaises(ValueError) as _:
            files.cached_download_abs_excel("640101", quarter="feb", year=2006)

    def test_cached_download_abs_excel_by_date_future(self):
        future = datetime.now() + timedelta(days=100)  # The next quarter is sure to not yet be released

        with patch("sys.stderr", new=StringIO()) as fake_out:
            files.cached_download_abs_excel_by_date("640101", future)
            self.assertIn(f"CPI data for {future} not available.", fake_out.getvalue())
