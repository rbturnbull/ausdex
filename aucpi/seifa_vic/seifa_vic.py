from aucpi import seifa_vic
from .data_wrangling import preprocess_victorian_datasets
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd
from typing import Union

def _make_nan(x):
	if type(x) != np.array:
		x = np.array(x)
	return x*np.nan

def _make_cache_key(suburb, metric, fill_value, **kwargs):
	test_kwargs = {'test1':'test2'}
	key_val_list = [f'{str(key)}_{str(kwargs[key])}' for key in sorted(list(kwargs.keys()))]
	return f"{suburb}_{metric}_{fill_value}_" + '_'.join(key_val_list)

class SeifaVic:
	"""This object loads, or creates the combined dataset for the SEIFA_VIC interpolations
	"""

	def __init__(self, force_rebuild=False):
		"""initialising SeifaVic object

		Args:
			force_rebuild (bool, optional): forces the reconstruction of the combined dataset if already built and saved in user data. Defaults to False.
		"""
		self.metrics = ['ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', 'uirsa_score']
		self.force_rebuild = force_rebuild
		self.interp_cache = {}
	def _load_data(self):
		"""loads the preprocessed victorian dataset if it hasn't been loaded already
		"""
		if 'df' not in self.__dict__:
			# print('loading data')
			self.df = preprocess_victorian_datasets(force_rebuild=self.force_rebuild)
			for col in ['year'] + self.metrics:
				self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

	
	
	def get_suburb_data(self, suburb: str):
		"""returns the dataset (self.df) filtered to a suburb

		Args:
			suburb (str): suburb that dataset will be filtered too(must be all caps)

		Returns:
			pd.DataFrame: filtered dataframe with only the data from that suburb
		"""
		return self.df[self.df['Site_suburb']==suburb]

	def build_interpolator(self, suburb: str, metric: str,fill_value: Union[str, np.array, tuple], **kwargs) -> interp1d:
		"""this function builds an interpolator with the "year" column as the x, and the metric column as the y

		Args:
			suburb (str): suburb that dataset will be filtered too(must be all caps)
			metric (str): 'ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score', the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage. 
		 
			fill_value (Union[str, np.array, tuple]): Specifies the values returned outside the range of the ABS census datasets. It can be "extrapolate" to extrapolate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument.

		Returns:
			scipy.interpolate.interp1d: interpolator object for the suburb and metric
		"""
		df = self.get_suburb_data(suburb).dropna(subset=[metric]).sort_values('year')
		if fill_value == 'boundary_value':

			fill_value = (df[metric].values[0], df[metric].values[-1])
		
		kwargs['bounds_error'] = False
		if df.shape[0] >1:
			return interp1d(df['year'].values, df[metric].values,fill_value=fill_value, **kwargs)
		else:
			return _make_nan
	
	def _should_build_interps(self, fill_value, **kwargs):
		if 'interpolators' not in self.__dict__:
			return True
		else:
			if (fill_value == self.fill_value) & (kwargs == self.kwargs):
				return False
			else:
				return True

	def _build_interps(self,fill_value: Union[str, np.array, tuple]  = 'extrapolate', **kwargs ) -> dict:
		"""private method to build a list of interpolators

		Args:
			fill_value (Union[str, np.array, tuple], optional): [description]. Defaults to 'extrapolate'.

		Returns:
			dict: [description]
		"""
		self._load_data()

		if self._should_build_interps(fill_value, **kwargs):
			self.fill_value = fill_value
			self.kwargs = kwargs
			self.interpolators = {}
			for metric in self.metrics:
				self.interpolators[metric] = {}
				for suburb in self.df['Site_suburb'].unique():
					self.interpolators[metric][suburb] = self.build_interpolator(suburb, metric, fill_value=fill_value, **kwargs)

		
	
	def get_seifa_interpolation(self,year_values: Union[int,float,np.array, list], suburb: str,metric: str, fill_value: Union[str, np.array, tuple]  = 'null', **kwargs )-> Union[float, np.array]:
		"""method to get an interpolated estimate of a SEIFA score for each victorian suburb from Australian Bureau of statistics data

		Args:
			year_values (Union[int,float,np.array, list]): The year or array of year values you want interpolated.
			suburb (str): The name of the suburb that you want the data interpolated for (capitalisation doesn't matter).
			metric (str): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage. 
			fill_value (Union[str, np.array, tuple], optional): Specifies the values returned outside the range of the ABS census datasets. It can be "extrapolate" to extraplate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'extrapolate'.
			**kwargs(dict-like): additional keyword arguments for scipy.interpolate.interp1D object.

		Returns:
			Union[float, np.array]: The interpolated value (s) of that seifa variable at that year(s). np.array if year_value contains multiple years.
		"""
		assert isinstance(year_values, (int, float, list, np.float32, np.int32 ,np.array, pd.Series))
		self._load_data()
		return self.build_interpolator(suburb, metric, fill_value=fill_value, **kwargs)(year_values)

	def get_seifa_interpolation_batch(self,year_values: Union[int,float,np.array, list], suburb: str,metric: str, fill_value: Union[str, np.array, tuple]  = 'null', **kwargs )-> Union[float, np.array]:
		assert isinstance(year_values, (int, float, list, np.float32, np.int32 ,np.array, pd.Series))
		self._load_data()
		self._build_interps(fill_value=fill_value, **kwargs)
		interps = self.interpolators[metric]
		if type(suburb) == list:
			suburb = np.array(suburb)
		suburb = np.char.upper(suburb)
		input_df = pd.DataFrame({'suburb': suburb, 'years':year_values})
		input_df['interpolated'] = 0.

		for sub in input_df.suburb.unique():
			sub_mask = input_df['suburb']==sub
			input_df.loc[sub_mask, 'interpolated'] = interps[sub](input_df.loc[sub_mask, 'years'])

		
		return input_df['interpolated'].values




seifa_vic = SeifaVic()


def interpolate_vic_suburb_seifa(year_values,suburb, metric, fill_value='extrapolate',  **kwargs )-> np.array or float:
	"""function to get an interpolated estimate of a SEIFA score for each victorian suburb from Australian Bureau of statistics data

	Args:
		year_values (int, float, np.ndarray like): The year or array of year values you want interpolated.
		suburb (str): The name of the suburb that you want the data interpolated for (capitalisation doesn't matter).
		metric (List['ier_score', 'irsd_score','ieo_score','irsad_score','rirsa_score', ‘uirsa_score']): the name of the seifa_score variable, options are include `irsd_score` for index of relative socio economic disadvantage,`ieo_score` for the index of education and opportunity, `ier_score` for an index of economic resources, `irsad_score` for index of socio economic advantage and disadvantage,`uirsa_score` for the urban index of relative socio economic advantage, `rirsa_score` for the rural index of relative socio economic advantage. 
		fill_value (str, np.array or tuple): Specifies the values returned outside the range of the ABS census datasets. It can be "extrapolate" to extraplate past the extent of the dataset or "boundary_value" to use the closest datapoint, or an excepted response for scipy.interpolate.interp1D fill_value keyword argument. Defaults to 'extrapolate'.
		**kwargs(dict-like): additional keyword arguments for scipy.interpolate.interp1D object.
	Returns:
		Union[float, np.array]: The interpolated value (s) of that seifa variable at that year(s). np.array if year_value contains multiple years.
	"""
	if type(suburb) == str:
		out = seifa_vic.get_seifa_interpolation(year_values,suburb.upper(), metric, 
									fill_value=fill_value, **kwargs)
	else:
		out = seifa_vic.get_seifa_interpolation_batch(year_values,suburb, metric, 
									fill_value=fill_value, **kwargs)
	if out.size == 1:
		out = out.item()
	return out