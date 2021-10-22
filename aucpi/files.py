from pathlib import Path
from appdirs import user_cache_dir

import urllib.request


def get_cached_path(filename):
    cache_dir = Path(user_cache_dir("aucpi"))
    cache_dir.mkdir(exist_ok=True, parents=True)
    return cache_dir / filename


def cached_download(url: str, local_path: (str, Path), attempt_download=True) -> None:
    """
    Downloads a file if a local file does not already exist.

    Args:
        url: The url of the file to download.
        local_path: The local path of where the file should be. If this file isn't there or the file size is zero then this function downloads it to this location.

    Raises:
        Exception: Raises an exception if it cannot download the file.

    """

    local_path = Path(local_path)
    if (not local_path.exists() or local_path.stat().st_size == 0) and attempt_download:
        try:
            print(f"Downloading {url} to {local_path}")
            urllib.request.urlretrieve(url, local_path)
        except:
            raise Exception(f"Error downloading {url}")

    if not local_path.exists() or local_path.stat().st_size == 0:
        raise Exception(f"Error reading {local_path}")
