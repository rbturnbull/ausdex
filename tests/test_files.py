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
