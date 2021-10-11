from pandas.io.pytables import SeriesFixed
from .data_io import load_gis_data, load_csv_data, load_xls_data, load_shapefile_data, get_cached_path, load_victorian_suburbs_metadata, load_aurin_data
from geopandas.tools import sjoin
import geopandas as gpd
import pandas as pd

def group_repeat_names_vic(x):
    if x['loc_pid'] == 'VIC2961':
        return 'BELLFIELD - GRAMPIANS'
    elif x['loc_pid'] == 'VIC2967':
        return 'BELLFIELD - BANYULE'
    elif x['loc_pid'] == 'VIC2976':
        return 'HAPPY VALLEY - SWAN HILL'
    elif x['loc_pid'] == 'VIC2984':
        return 'HILLSIDE - MELTON'
    elif x['loc_pid'] == 'VIC2990':
        return 'REEDY CREEK - MITCHELL'
    elif x['loc_pid'] == 'VIC2969':
        return 'SPRINGFIELD - MACEDON RANGES'
    elif x['loc_pid'] == 'VIC2963':
        return 'STONY CREEK - HEPBURN'
    else:
        return x['suburb_name_combined']

def parse_duplicates_from_victorian_councils(suburbs, councils):

	vic_locations = load_victorian_suburbs_metadata()
	duplicated_suburbs = vic_locations[vic_locations.duplicated(subset=['locality_name'])]['locality_name'].unique()
	dup_suburbs_gdf = suburbs[suburbs['vic_loca_2'].apply(lambda x: x in duplicated_suburbs[:-1])]
	
	dup_suburbs_join = sjoin(dup_suburbs_gdf.to_crs('EPSG:4326'), councils.to_crs('EPSG:4326'), how="left")
	dup_suburbs_join['suburb_name_combined'] = dup_suburbs_join.apply(lambda x: f'{x["vic_loca_2"]} - {x["vic_lga__2"]}', axis=1)
	# note, this was identifired 
	dup_suburbs_join['fixed_multinames'] = dup_suburbs_join.apply(group_repeat_names_vic, axis=1)
	dup_suburbs_join_dis = dup_suburbs_join.drop_duplicates(subset=['fixed_multinames'])
	double_name_converter = {code:name for code, name in zip(dup_suburbs_join_dis.loc_pid.values, dup_suburbs_join_dis.fixed_multinames.values)}

	def change_multinames(x, cdict = double_name_converter):
		if x['loc_pid'] in cdict:
			return cdict[x['loc_pid'] ]
		else:
			return x['vic_loca_2']
	suburbs['fixed_names'] = suburbs.apply(change_multinames, axis=1)
	suburbs.rename(columns={'fixed_names':'Site_suburb'}, inplace=True)
	return suburbs

def wrangle_victorian_gis_data(parse_duplicates = True):
	suburbs = load_gis_data('victoria_suburbs')
	councils = load_gis_data('victoria_councils')
	if parse_duplicates == True:
		suburbs = parse_duplicates_from_victorian_councils(suburbs, councils)
	return suburbs, councils

def convert_spreadsheet_colnames(df):
	name_change = {}
	drop_cols = []
	for col in df.columns:
		if ('Suburb (SSC) Code' in col) or ('state suburb code (ssc)' in col.lower()):
			name_change[col] = 'suburb_code'
		elif 'Suburb (SSC) Name' in col:
			name_change[col] = 'suburb_name'
		elif 'Economic Resources - Score' in col:
			name_change[col] = 'ier_score'
		elif 'Education and Occupation - Score' in col:
			name_change[col] = 'ieo_score'
		elif 'Resident Population' in col:
			name_change[col] = 'population'
		elif "Relative Socio-economic Disadvantage - Score" in col:
			name_change[col] = 'irsd_score'
		elif "Relative Socio-economic Advantage and Disadvantage - Score" in col:
			name_change[col] = 'irsad_score'
		elif 'Census Collection District' in col:
			name_change[col] = 'cd_code'
		else:
			drop_cols.append(col)
	# print(drop_cols, name_change)
	return df.rename(columns = name_change).drop(columns=drop_cols)

        
def suburb_name_fix(x):
    if type(x) == str:
        if '(' in x:
            x = x.split('(')[0]
        return x.upper().strip()
    else:
        return x   	

def wrangle_abs_spreadsheet_datasets(dataset):
	df = load_xls_data(dataset, sheet_name = 'Table 1', header=[4,5])
	df.columns= [' - '.join(i) for i in df.columns]
	df = convert_spreadsheet_colnames(df)
	return df

def get_2016_vic_suburb_name_fixer():
	name_fixer_dict_2016 = {
    #2016
    'Ascot (Ballarat - Vic.)': 'ASCOT - BALLARAT',
    'Ascot (Greater Bendigo - Vic.)': 'ASCOT - GREATER BENDIGO',
    'Bellfield (Banyule - Vic.)': 'BELLFIELD - BANYULE',
    'Big Hill (Greater Bendigo - Vic.)': 'BIG HILL - GREATER BENDIGO',
    'Big Hill (Surf Coast - Vic.)': 'BIG HILL - SURF COAST',
    'Fairy Dell (Campaspe - Vic.)': 'FAIRY DELL - CAMPASPE',
    'Golden Point (Ballarat - Vic.)': 'GOLDEN POINT - BALLARAT',
    'Golden Point (Mount Alexander - Vic.)': 'GOLDEN POINT - MOUNT ALEXANDER', 
    'Happy Valley (Golden Plains - Vic.)': 'HAPPY VALLEY - GOLDEN PLAINS',
    'Happy Valley (Swan Hill - Vic.)': 'HAPPY VALLEY - SWAN HILL',
    'Hillside (East Gippsland - Vic.)': 'HILLSIDE - EAST GIPPSLAND',
    'Hillside (Melton - Vic.)': 'HILLSIDE - MELTON',
    'Killara (Wodonga - Vic.)': 'KILLARA - WODONGA',
    'Merrijig (Mansfield - Vic.)': 'MERRIJIG - MANSFIELD',
    'Moonlight Flat (Central Goldfields - Vic.)': 'MOONLIGHT FLAT - CENTRAL GOLDFIELDS',
    'Moonlight Flat (Mount Alexander - Vic.)':'MOONLIGHT FLAT - MOUNT ALEXANDER',
    'Myall (Gannawarra - Vic.)':'MYALL - GANNAWARRA',
    'Newtown (Golden Plains - Vic.)':'NEWTOWN - GOLDEN PLAINS',
    'Newtown (Greater Geelong - Vic.)':'NEWTOWN - GREATER GEELONG',
    'Springfield (Macedon Ranges - Vic.)':'SPRINGFIELD - MACEDON RANGES',
    'Stony Creek (South Gippsland - Vic.)':'STONY CREEK - SOUTH GIPPSLAND',
    'Thomson (Greater Geelong - Vic.)':'THOMSON - GREATER GEELONG'
	}
	return name_fixer_dict_2016

def get_ssc_2011(code_begin, code_end):
	ssc_2011 = load_csv_data('state_suburb_codes_2011', zipped=True)
	ssc_2011 = ssc_2011[(ssc_2011['SSC_CODE_2011'] >= code_begin) &( ssc_2011['SSC_CODE_2011'] <code_end)]
	ssc_2011 = ssc_2011.drop_duplicates(subset='SSC_CODE_2011')
	return ssc_2011


def get_victorian_abs_spreadsheets():
	df_2011 = wrangle_abs_spreadsheet_datasets('seifa_suburb_2011')
	df_2016 = wrangle_abs_spreadsheet_datasets('seifa_suburb_2016')
	return df_2011, df_2016

def combine_victorian_abs_spreadsheets(df_2011=None, df_2016=None):
	if (type(df_2011) == type(None)) |(type(df_2016) == type(None) ): 
		df_2011, df_2016 = get_victorian_abs_spreadsheets()
	ssc_2011 = get_ssc_2011(20000,30000)
	df_out_l = []
	for year, df_rename in zip([2016, 2011], [ df_2016, df_2011]):
		print(f'processing year {year}')
		df_rename['suburb_code'] = pd.to_numeric(df_rename['suburb_code'],downcast='integer', errors='coerce')
		df_rename.dropna(subset=['suburb_code'], inplace=True)
		df_rename = df_rename[(df_rename['suburb_code'] < 30000) & (df_rename['suburb_code'] > 19999)]
		
		if year == 2011:
			df_rename = df_rename.merge(ssc_2011[['SSC_CODE_2011','SSC_NAME_2011']], left_on='suburb_code', right_on='SSC_CODE_2011', how='left')
			df_rename.rename(columns={"SSC_NAME_2011":'suburb_name'}, inplace=True)

		df_rename['year'] = year
		df_out_l.append(df_rename)
	
	df_comb = pd.concat(df_out_l)
	name_fixer_dict_2016 = get_2016_vic_suburb_name_fixer()

	def fix_2016_multisuburbs(x, cdict = name_fixer_dict_2016):
		if x['suburb_name'] in cdict:
			return cdict[x['suburb_name']]
		else:
			return x['suburb_name']
	
	df_comb['suburb_name_fix'] = df_comb.apply(fix_2016_multisuburbs, axis=1)

	df_comb['Site_suburb'] = df_comb.suburb_name_fix.apply(suburb_name_fix)

	return df_comb

def combine_2006_dataset():
	CD_2006 = load_shapefile_data('seifa_2006_cd_shapefile')
	seifa_2006 = wrangle_abs_spreadsheet_datasets('seifa_2006_cd')
	CD_2006['CD_CODE06'] = pd.to_numeric(CD_2006['CD_CODE06']).astype('int')
	seifa_2006.columns = ['cd_code', 'irsad_score', 'irsd_score', 'ier_score', 'ieo_score', 'population']
	seifa_2006['cd_code'] = pd.to_numeric(seifa_2006['cd_code'], errors='coerce')
	seifa_2006.dropna(subset=['cd_code'], inplace=True)
	seifa_2006['cd_code'] = seifa_2006['cd_code'].astype('int')
	seifa_2006 = seifa_2006[(seifa_2006['cd_code']> 2000000) & (seifa_2006['cd_code'] < 3000000)]
	CD_2006 = CD_2006.merge(seifa_2006[['cd_code', 'ier_score', 'ieo_score', 'population']], left_on ='CD_CODE06', right_on = 'cd_code', how='left' )
	return CD_2006


def get_aurin_datasets_vic():
	# will eventual give out gdf_1986, 1991, 1996 from aurin
	# gdf_2001 = gpd.read_file('/Users/garberj/data/vbadata_SEIFA/ABS_-_Socio-Economic_Indexes_for_Areas__SEIFA___CD__2001.json/data2516898914808603983.json')
	# gdf_1996 = gpd.read_file('/Users/garberj/data/vbadata_SEIFA/ABS_-_Socio-Economic_Indexes_for_Areas__SEIFA___CD__1996.json/data7336844287967253519.json')
	# gdf_1991 = gpd.read_file('/Users/garberj/data/vbadata_SEIFA/ABS_-_Socio-Economic_Indexes_for_Areas__SEIFA___CD__1991.json/data354505989715425060.json')
	# gdf_1986= gpd.read_file('/Users/garberj/data/vbadata_SEIFA/ABS_-_Socio-Economic_Indexes_for_Areas__SEIFA___CD__1986.json/data7355794508419511170.json')
	
	gdf_1986, gdf_1991, gdf_1996, gdf_2001 = load_aurin_data(['seifa_1986_aurin', 'seifa_1991_aurin', 'seifa_1996_aurin', 'seifa_2001_aurin'])
	return gdf_1986, gdf_1991, gdf_1996, gdf_2001


def convert_cds_colnames_gdf(df):
	name_change = {}
	drop_cols = []
	keep_cols = ['geometry', 'ier_score', 'ieo_score']
	for col in list(df.columns):
		# print(col) 
		if 'index_of_economic_resources' in col:
			name_change[col] = 'ier_score'

		elif 'index_of_education_and_occupation' in col:
			name_change[col] = 'ieo_score'
		elif 'index_of_relative_socio_economic_disadvantage' in col:
			name_change[col] = 'irsd_score'
		elif 'rural_index_of_relative_socio_economic_advantag' in col:
			name_change[col] = 'rirsa_score'
		elif 'urban_index_of_relative_socio_economic_advantag' in col:
			name_change[col] = 'uirsa_score'		
		elif '_population' in col:
			name_change[col] = 'population'
		elif 'isad_score' in col:
			name_change[col] = 'irsad_score'
		elif col not in keep_cols:
			drop_cols.append(col)
	
	return df.rename(columns = name_change).drop(columns=drop_cols)

def calc_area(gdf, crs ='EPSG:32756'):
    return gdf.geometry.to_crs(crs).area

def w_avg(df, values, weights):
    
    d = df[values]
    w = df[weights]
    return (d * w).sum() / w.sum()

def preprocess_victorian_datasets(force_rebuild = False):
	preprocessed_path = get_cached_path('preprocessed_vic_seifa.csv')
	if (preprocessed_path.exists() == False) or (force_rebuild==True):
		df_comb =combine_victorian_abs_spreadsheets()
		# print('df_comb max year before combining with gdf', df_comb.year.max())
		gdf_2006 = combine_2006_dataset()
		gdf_1986, gdf_1991, gdf_1996, gdf_2001 = get_aurin_datasets_vic()
		suburbs_coordinates, _ = wrangle_victorian_gis_data()
		concat_stack = []
		for year,df in zip([1986, 1991, 1996, 2001, 2006],[gdf_1986, gdf_1991, gdf_1996, gdf_2001, gdf_2006]):
			print(f'processing {year}')
			df_rename = convert_cds_colnames_gdf(df)
			df_union = gpd.overlay(df_rename.to_crs("EPSG:4326"), suburbs_coordinates.to_crs('EPSG:4326'))
			df_union['area'] = calc_area(df_union)
			col_dict = {}
			for col in ['ieo_score', 'ier_score', 'irsad_score','rirsa_score', 'uirsa_score', 'irsd_score']:
				if col in df_union.columns:
					col_dict[col]  = df_union.groupby('Site_suburb').apply(w_avg, col, 'area')
			

			out = pd.DataFrame(col_dict).reset_index()
			out['year'] = year
			concat_stack.append(out)
		combined = pd.concat(concat_stack)
		total_df = pd.concat([combined, df_comb])
		total_df.to_csv(preprocessed_path, index=False)
	else:
		total_df = pd.read_csv(preprocessed_path)
	return total_df