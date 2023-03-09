from pandas import DataFrame

def filter_main_group_callable(main_group: str):
	def inner(df: DataFrame):
		return df.main_group == main_group_name
	return inner