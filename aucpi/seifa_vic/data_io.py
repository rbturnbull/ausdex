import geopandas as gpd
import pandas as pd
from pathlib import Path
from aucpi.files import cached_download
from appdirs import user_cache_dir
from pathlib import Path
import zipfile
import os

def get_cached_path(file_name):
	cache_dir= Path(user_cache_dir('aucpi'))
	cache_dir.mkdir(exist_ok=True, parents=True)
	return cache_dir/file_name

def get_data_links():
	out = dict(
		victoria_suburbs = 'https://data.gov.au/geoserver/vic-suburb-locality-boundaries-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_af33dd8c_0534_4e18_9245_fc64440f742e&outputFormat=json',
		victoria_councils = 'https://data.gov.au/geoserver/vic-local-government-areas-psma-administrative-boundaries/wfs?request=GetFeature&typeName=ckan_bdf92691_c6fe_42b9_a0e2_a4cd716fa811&outputFormat=json',
		seifa_suburb_2011= 'https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&2033.0.55.001%20ssc%20indexes.xls&2033.0.55.001&Data%20Cubes&F40D0630B245D5DCCA257B43000EA0F1&0&2011&05.04.2013&Latest',
		seifa_suburb_2016 = 'https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&2033055001%20-%20ssc%20indexes.xls&2033.0.55.001&Data%20Cubes&863031D939DE8105CA25825D000F91D2&0&2016&27.03.2018&Latest',
		victorian_suburb_list = Path(__file__)/'metadata'/'victorian_locations.csv',
		state_suburb_codes_2011 = 'https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1270055003_ssc_2011_aust_csv.zip&1270.0.55.003&Data%20Cubes&414A81A24C3049A8CA2578D40012D50C&0&July%202011&22.07.2011&Previous',
		seifa_2006_cd = 'https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&2033055001_%20seifa,%20census%20collection%20districts,%20data%20cube%20only,%202006.xls&2033.0.55.001&Data%20Cubes&6EFDD4FA99C28C4ECA2574170011668A&0&2006&26.03.2008&Latest',
		seifa_2006_cd_shapefile = 'https://www.abs.gov.au/AUSSTATS/subscriber.nsf/log?openagent&1259030002_cd06avic_shape.zip&1259.0.30.002&Data%20Cubes&D62E845F621FE8ACCA25795D002439BB&0&2006&06.12.2011&Previous',
		seifa_2001_aurin = 'aurin:datasource-AU_Govt_ABS-UoM_AURIN_DB_3_seifa_cd_2001',
		
	)

	return out

def download_dataset(dataset, suffix, links, should_unzip=False):
	local_path = get_cached_path(f"{dataset}.{suffix}")
	cached_download(links[dataset], local_path)
	if should_unzip == True:
		new_local_path = get_cached_path(f"{dataset}_unzipped")
		with zipfile.ZipFile(local_path, 'r') as zip_ref:
   			zip_ref.extractall(new_local_path)
		os.remove(local_path)
		return new_local_path
	else:
		return local_path
			
def load_gis_data(dataset = ' victoria_suburbs', **kwargs):
	links = get_data_links()
	local_path = download_dataset(dataset, 'geojson', links)
	
	return gpd.read_file(local_path, **kwargs)

def load_xls_data(dataset='seifa_suburb_2016', **kwargs):
	links = get_data_links()
	local_path = download_dataset(dataset, 'xls', links)

	return pd.read_excel(links[dataset], **kwargs)

def load_csv_data(dataset='victorian_suburb_list', zipped=False, **kwargs):
	links = get_data_links()
	if zipped == True: suffix = '.csv.zip'
	else: suffix = '.csv'
	local_path = download_dataset(dataset, suffix, links)
	return pd.read_csv(local_path, **kwargs)

def load_shapefile_data(dataset='seifa_2006_cd_shapefile'):
	links = get_data_links()
	local_path = download_dataset(dataset, '', links, should_unzip=True)
	shpfile_path = [x for x in local_path.iterdir() if 'shp' in x.name]
	return gpd.read_file(shpfile_path[0])



