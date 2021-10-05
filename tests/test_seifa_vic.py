import unittest
from aucpi.seifa_vic.data_wrangling import preprocess_victorian_datasets 


class TestSeifaVicSetup(unittest.TestCase):
	
	def test_preprocess_victorian_datasets(self):
		df = preprocess_victorian_datasets(force_rebuild=True)
		
		cols = ['ieo_score', 'ier_score', 'irsad_score','rirsa_score', 'uirsa_score', 'irsd_score', 'year', 'Site_suburb']
		for col in cols:
			assert col in df.columns,f"{col} not in dataset"
	

class TestSeifaVicInterpolation(unittest.TestCase):
	def test_seifa_interpolation(self):
		from aucpi.seifa_vic.seifa_vic import interpolate_vic_suburb_seifa

		value = interpolate_vic_suburb_seifa(1987, 'ABBOTSFORD', 'ier_score')
		print(value)
