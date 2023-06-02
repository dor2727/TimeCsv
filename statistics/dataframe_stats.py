from pandas import DataFrame

from ..utils.times import seconds_to_time_str, Seconds, Days

class DFStats(object):
	def __init__(self, df: DataFrame):
		self.df = df
	
	def stats(self):
		return "Cool stats"
