import sys
from pathlib import Path
from appdirs import user_cache_dir
from typing import Union
import urllib.request
from datetime import datetime, timedelta


ACCEPTED_QUARTERS = ("mar", "jun", "sep", "dec")


class DownloadError(Exception):
    pass


def get_cached_path(filename: str) -> Path:
    """
    Returns a path in the ausdex directory in the user's cache.

    File may or may not exist.
    """
    cache_dir = Path(user_cache_dir("ausdex"))
    cache_dir.mkdir(exist_ok=True, parents=True)
    return cache_dir / filename


def cached_download(url: str, local_path: Union[str, Path], force: bool = False, verbose:bool = False) -> None:
    """
    Downloads a file if a local file does not already exist.

    Args:
        url (str): The url of the file to download.
        local_path (str, Path): The local path of where the file should be.
            If this file isn't there or the file size is zero then this function downloads it to this location.
        force (bool): Whether or not the file should be forced to download again even if present in the local path.
            Default False.

    Raises:
        DownloadError: Raises an exception if it cannot download the file.
        IOError: Raises an exception if the file does not exist or is empty after downloading.
    """
    local_path = Path(local_path)
    if (not local_path.exists() or local_path.stat().st_size == 0) or force:
        try:
            urllib.request.urlretrieve(url, local_path)
        except Exception:
            raise DownloadError(f"Error downloading {url}")

    if not local_path.exists() or local_path.stat().st_size == 0:
        raise IOError(f"Error reading {local_path}")


def cached_download_abs(
    id: str,
    quarter: str,
    year: Union[int, str],
    extension: str,
    local_path: Union[Path, str, None] = None,
    force: bool = False,
) -> Path:
    """
    Downloads a file from the ABS if a local file does not already exist.

    Args:
        id (str): The ABS id for the datafile. For Australian Consumer Price Index the ID is 640101.
        quarter (str): The quarter of the file in question. One of "mar", "jun", "sep", or "dec".
        year (str, int): The year for the file in question.
        extension (str): The extension of the file in question.
        local_path (Path, str, optional): The path to where the file should be downloaded.
            If None, then it is downloaded in the user's cache directory.
        force (bool): Whether or not the file should be forced to download again even if present in the local path.
        local_path (str, Path): The local path of where the file should be.
            If this file isn't there or the file size is zero then this function downloads it to this location.
        force (bool): Whether or not the file should be forced to download again even if present in the local path.

    Raises:
        ValueError: If the value for `quarter` cannot be understood.
        DownloadError: Raises an exception if it cannot download the file.
        IOError: Raises an exception if the file does not exist or is empty after downloading.

    Returns:
        Path: The path to the downloaded ABS datafile.
    """
    quarter = quarter.lower()[:3]
    if quarter not in ACCEPTED_QUARTERS:
        raise ValueError(f"Cannot understand quarter {quarter}.")

    if (year == 2021 and quarter == 'dec') or year > 2021:
        extension = "xlsx"
    else:
        extension = "xls"

    if (year == 2022 and quarter in ['jun', 'dec']) or year > 2022:
        online_dir = f"{quarter}-quarter-{year}"
    else:
        online_dir = f"{quarter}-{year}"
    

    local_path = local_path or get_cached_path(f"{id}-{quarter}-{year}.{extension}")
    local_path = Path(local_path)
    
    url = f"https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/{online_dir}/{id}.{extension}"
    cached_download(url, local_path, force=force)

    return local_path


def cached_download_abs_excel(
    id: str, quarter: str, year: Union[str, int], local_path: Union[Path, str, None] = None, force: bool = False
) -> Path:
    """
    Gets am Excel file from the Australian Burau of Statistics.

    First it tries the extension `xlsx` and then falls back to `xls`.

    Args:
        id (str): The ABS id for the datafile. For Australian Consumer Price Index the ID is 640101.
        quarter (str): The quarter of the file in question. One of "mar", "jun", "sep", or "dec".
        year (str, int): The year for the file in question.
        local_path (Path, str, optional): The path to where the file should be downloaded.
            If None, then it is downloaded in the user's cache directory.
        force (bool): Whether or not the file should be forced to download again even if present in the local path.
            Default False.

    Raises:
        ValueError: Raises this error if the quarter cannot be understood.

    Returns:
        Path: The path to the cached ABS datafile
    """
    local_path = cached_download_abs(
        quarter=quarter, year=year, id=id, extension="xlsx", local_path=local_path, force=force
    )

    return local_path


def cached_download_abs_excel_by_date(
    id: str, date: Union[datetime, None] = None, local_path: Union[Path, str, None] = None, force: bool = False
) -> Path:
    """
    Gets a datafile from the Australian Burau of Statistics before a specific date.

    Args:
        id (str): The ABS id for the datafile. For Australian Consumer Price Index (CPI) the ID is 640101.
        date (datetime, optional): The date before which the CPI data should be valid.
            If not provided, then it uses today's date download get the latest file.
        local_path (Path, str, optional): The path to where the file should be downloaded.
            If None, then it is downloaded in the user's cache directory.
        force (bool): Whether or not the file should be forced to download again even if present in the local path.
            Default False.

    Returns:
        Path: The path to the cached ABS datafile.
    """
    date = date or datetime.now()
    file = None
    while file is None and date > datetime(1948, 1, 1):
        year = date.year
        quarter_index = (date.month - 3) // 3
        if quarter_index == -1:
            quarter_index = 3
            year -= 1
        quarter = ACCEPTED_QUARTERS[quarter_index]

        try:
            file = cached_download_abs_excel(id, quarter, year, local_path=local_path, force=force)
            break
        except (DownloadError, IOError):
            print(f"WARNING: CPI data for Quarter {quarter.title()} {year} not yet available.", file=sys.stderr)

        date -= timedelta(days=89)  # go back approximately a quarter

    return file


def cached_download_cpi(
    *, date: Union[datetime, None] = None, local_path: Union[Path, str, None] = None, force: bool = False
) -> Path:
    """
    Returns the path to the latest cached file with the Australian Consumer Price Index (CPI) data.

    It downloads the file if it does not exist already. The ABS id of this file is "640101".

    Args:
        date (datetime, optional): The date before which the CPI data should be valid.
            If not provided, then it uses today's date download get the latest file.
        local_path (Path, str, optional): The path to where the file should be downloaded.
            If None, then it is downloaded in the user's cache directory.
        force (bool): Whether or not the file should be forced to download again even if present in the local path.
            Default False.

    Returns:
        Path: The path to the cached datafile.
    """
    CPI_FILE_ID = "640101"
    return cached_download_abs_excel_by_date(id=CPI_FILE_ID, date=date, local_path=local_path, force=force)
