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

			fill_value = (df[variable].values[0], df[variable].values[-1])
		
		kwargs['bounds_error'] = False
		return interp1d(df['year'].values, df[variable].values,fill_value=fill_value, **kwargs)
	
	def get_seifa_data(self,year_values, suburb,variable, fill_value = 'extrapolate', **kwargs ):
		assert isinstance(year_values, (int, float, list, np.float32, np.int32 ,np.array, pd.Series))
		
		return self.build_interpolator(suburb, variable, fill_value=fill_value, **kwargs)(year_values)






def interpolate_vic_suburb_seifa(year_values,suburb, metric, fill_value='extrapolate',  **kwargs )-> np.array or float:
	"""function to get an interpolated estimate of a SEIFA score for each victorian suburb from Australian Bureau of statistics data

	Args:
		year_values (int, float, np.ndarray like): The year or array of year values you want interpolated.
		suburb (str): The name of the suburb that you want the data interpolated for (capitalisation doesn't matter).
		metric (List['ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score']): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage. 
		fill_value (str, np.array or tuple): Specifies the values returned outside the range of the ABS census datasets. It can be "extrapolate" to extraplate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'extrapolate'.
		**kwargs(dict-like): additional keyword arguments for scipy.interpolate.interp1D object.
	Returns:
		np.array or float: The interpolated value (s) of that seifa variable at that year(s). np.array if year_value contains multiple years.
	"""
	seifa_vic = SeifaVic()
	out = seifa_vic.get_seifa_data(year_values,suburb.upper(), metric, 
								   fill_value=fill_value, **kwargs)
	if out.size == 1:
		out = out.item()
	return out