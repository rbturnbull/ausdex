import geopandas as gpd
import pandas as pd
from pathlib import Path
from ausdex.files import cached_download, get_cached_path
from pathlib import Path
import zipfile
import os
import json
from getpass import getpass
from owslib.wfs import WebFeatureService


def open_geopandas(file, **kwargs):
    return gpd.read_file(file, **kwargs)


def get_data_links():
    out = dict(
        victoria_suburbs="https://data.gov.au/geoserver/vic-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_af33dd8c_0534_4e18_9245_fc64440f742e&outputFormat=json",
        victoria_councils="https://data.gov.au/geoserver/vic-local-government-areas-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_bdf92691_c6fe_42b9_a0e2_a4cd716fa811&outputFormat=json",
        # seifa_suburb_2011="https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&2033.0.55.001%20ssc%20indexes.xls&2033.0.55.001&Data%20Cubes&F40D0630B245D5DCCA257B43000EA0F1&0&2011&05.04.2013&Latest",
        # seifa_suburb_2016="https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&2033055001%20-%20ssc%20indexes.xls&2033.0.55.001&Data%20Cubes&863031D939DE8105CA25825D000F91D2&0&2016&27.03.2018&Latest",
        victorian_suburb_list=Path(__file__).parent
        / "metadata"
        / "victorian_locations.csv",
        # state_suburb_codes_2011="https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1270055003_ssc_2011_aust_csv.zip&1270.0.55.003&Data%20Cubes&414A81A24C3049A8CA2578D40012D50C&0&July%202011&22.07.2011&Previous",
        seifa_2006_cd="https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&2033055001_%20seifa,%20census%20collection%20districts,%20data%20cube%20only,%202006.xls&2033.0.55.001&Data%20Cubes&6EFDD4FA99C28C4ECA2574170011668A&0&2006&26.03.2008&Latest",
        seifa_2006_cd_shapefile="https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1259030002_cd06avic_shape.zip&1259.0.30.002&Data%20Cubes&D62E845F621FE8ACCA25795D002439BB&0&2006&06.12.2011&Previous",
        seifa_2001_aurin="aurin:datasource-AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_2001",
        seifa_1996_aurin="aurin:datasource-AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_1996",
        seifa_1991_aurin="aurin:datasource-AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_1991",
        seifa_1986_aurin="aurin:datasource-AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_1986",
        seifa_2016_sa1="https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&2033055001%20-%20sa1%20indexes.xls&2033.0.55.001&Data%20Cubes&40A0EFDE970A1511CA25825D000F8E8D&0&2016&27.03.2018&Latest",
        seifa_2011_sa1="https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&2033.0.55.001%20sa1%20indexes.xls&2033.0.55.001&Data%20Cubes&9828E2819C30D96DCA257B43000E923E&0&2011&05.04.2013&Latest",
        sa1_gis_2016="https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1270055001_sa1_2016_aust_shape.zip&1270.0.55.001&Data%20Cubes&6F308688D810CEF3CA257FED0013C62D&0&July%202016&12.07.2016&Latest",
        sa1_gis_2011="https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&1270055001_sa1_2011_aust_shape.zip&1270.0.55.001&Data%20Cubes&24A18E7B88E716BDCA257801000D0AF1&0&July%202011&23.12.2010&Latest",
    )

    return out


def unzip(local_path, new_path_name):
    with zipfile.ZipFile(local_path, "r") as zip_ref:
        zip_ref.extractall(new_path_name)
    os.remove(local_path)


def download_dataset(dataset, suffix, links, should_unzip=False):
    local_path = get_cached_path(f"{dataset}.{suffix}")
    if should_unzip == True:
        new_path_name = get_cached_path(f"{dataset}_unzipped")
        if new_path_name.exists() == True:
            return new_path_name
    cached_download(links[dataset], local_path)
    if should_unzip == True:
        unzip(local_path, new_path_name)
        return new_path_name
    else:
        return local_path


def load_gis_data(dataset=" victoria_suburbs", **kwargs):
    links = get_data_links()
    local_path = download_dataset(dataset, "geojson", links)

    return gpd.read_file(local_path, **kwargs)


def load_xls_data(dataset="seifa_suburb_2016", **kwargs):
    links = get_data_links()
    local_path = download_dataset(dataset, "xls", links)

    return pd.read_excel(local_path, **kwargs)


def load_shapefile_data(dataset="seifa_2006_cd_shapefile"):
    links = get_data_links()
    local_path = download_dataset(dataset, "", links, should_unzip=True)
    shpfile_path = [x for x in local_path.iterdir() if "shp" in x.name]
    return open_geopandas(shpfile_path[0])


def _get_input(msg):
    return input(msg)


def _get_getpass(msg):
    return getpass(msg)


def get_aurin_creds_path():
    return get_cached_path("aurin_creds.json")


def make_aurin_config():
    username = _get_input("Please enter your AURIN username: ")
    password = _get_getpass("Please enter your AURIN password: ")
    out = {"username": username, "password": password}

    path = get_aurin_creds_path()
    with open(path, "w") as file:
        json.dump(out, file)


def download_from_aurin(
    wfs_aurin, dataset, links, local_path, bbox=(96.81, -43.75, 159.11, -9.14)
):
    response = wfs_aurin.getfeature(
        typename=links[dataset],
        bbox=(96.81, -43.75, 159.11, -9.14),
        srsname="urn:x-ogc:def:crs:EPSG:4283",
        outputFormat="json",
    )

    with open(local_path, "w") as file:
        file.write(response.read().decode("UTF-8"))


def get_aurin_dataset(wfs_aurin, dataset, links):
    local_path = get_cached_path(dataset + ".geojson")
    if local_path.exists() == True:
        print(f"{dataset} already downloaded")
        return local_path
    download_from_aurin(wfs_aurin, dataset, links, local_path)

    return local_path


def get_config_ini():
    config_path = Path(__file__).parent.parent.parent / "config.ini"
    return config_path


def load_aurin_config():

    config_path = get_config_ini()

    if config_path.exists() == True:
        print("loading credentials from config.ini")
        import configparser

        parser = configparser.ConfigParser()

        parser.read(str(config_path))

        username = parser["aurin"]["username"]
        password = parser["aurin"]["password"]
        return dict(username=username, password=password)

    else:
        path = get_aurin_creds_path()
        if path.exists() == False:
            make_aurin_config()
        with open(path, "r") as file:
            creds = json.load(file)
        return creds


def get_aurin_wfs():
    creds = load_aurin_config()

    wfs_aurin = WebFeatureService(
        "http://openapi.aurin.org.au/wfs",
        version="1.1.0",
        username=creds["username"],
        password=creds["password"],
    )
    return wfs_aurin


def load_aurin_data(dataset: str or list):
    links = get_data_links()

    if type(dataset) == str:
        dataset = [dataset]
    local_paths = [get_cached_path(f"{ds}.geojson") for ds in dataset]
    all_downloaded = all([lp.exists() for lp in local_paths])
    if all_downloaded == True:
        return [gpd.read_file(lp) for lp in local_paths]
    else:
        wfs_aurin = get_aurin_wfs()
        outs = []
        for d in dataset:
            outs.append(open_geopandas(get_aurin_dataset(wfs_aurin, d, links)))
        return outs


def load_victorian_suburbs_metadata():
    links = get_data_links()
    return pd.read_csv(links["victorian_suburb_list"])
