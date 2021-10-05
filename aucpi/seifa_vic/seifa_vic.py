from .data_wrangling import preprocess_victorian_datasets
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd


class SeifaVic:

	def __init__(self, force_rebuild=False):
		self.df = preprocess_victorian_datasets(force_rebuild=force_rebuild)
	
	def get_suburb_data(self, suburb):
		return self.df[self.df['Site_suburb']==suburb]

	def build_interpolator(self, suburb, variable,fill_value, **kwargs):
		df = self.get_suburb_data(suburb).dropna(subset=[variable]).sort_values('year')
		if fill_value == 'boundary_value':
			fill_value = [df[variable].values[0], df[variable].values[-1]]
		return interp1d(df['year'].values, df[variable].values,fill_value=fill_value **kwargs)
	
	def get_seifa_data(self,year_values, suburb,variable, fill_value = 'extrapolate', **kwargs ):
		assert isinstance(year_values, (int, float, list, np.float32, np.int32 ,np.array, pd.Series))
		
		return self.build_interpolator(suburb, variable, fill_value=fill_value, **kwargs)(year_values)



seifa_vic = SeifaVic()


def interpolate_vic_suburb_seifa(year_values,suburb, variable, fill_value='extrapolate',  **kwargs )-> np.array:
	"""function to get an interpolated estimate of a SEIFA score for
	each victorian suburb from Australian Bureau of statistics data

	You can input 
	

    Args:
        year_values (int, float, np.ndarray like): The year or array of year values you want interpolated
        suburb (str): The name of the suburb that you want the data interpolated for
		variable (str): the name of the seifa_score variable, options are include 
		`irsd_score` for index of relative socio economic disadvantage,
		`ieo_score` for the index of education and opportunity, 
		`ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,
		`uirsa_score` for the urban index of relative socio economic advantage,
		`rirsa_score` for the rural index of relative socio economic advantage
		fill_value (str): 

    Returns:
        np.array: The interpolated value of the valueof that seifa variable at that year.

	"""
	out = seifa_vic.get_seifa_data(year_values,suburb, variable, 
								   fill_value=fill_value, **kwargs)
	return out