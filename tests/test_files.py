import unittest
import re
from unittest.mock import patch
from pathlib import Path

from ausdex import files


# def cached_download(url: str, local_path: (str, Path), attempt_download=True) -> None:

# 14    """

# 15    Downloads a file if a local file does not already exist.

# 16

# 17    Args:

# 18        url: The url of the file to download.

# 19        local_path: The local path of where the file should be. If this file isn't there or the file size is zero then this function downloads it to this location.

# 20

# 21    Raises:

# 22        Exception: Raises an exception if it cannot download the file.

# 23

# 24    """

# 25

# 26    local_path = Path(local_path)

# 27    if (not local_path.exists() or local_path.stat().st_size == 0) and attempt_download:

# 28        try:

# 29            print(f"Downloading {url} to {local_path}")

# 30            urllib.request.urlretrieve(url, local_path)

# 31        except:

# 32            raise Exception(f"Error downloading {url}")

# 33

# 34    if not local_path.exists() or local_path.stat().st_size == 0:

# 35        raise Exception(f"Error reading {local_path}")


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
