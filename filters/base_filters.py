from operator import and_
from functools import reduce
from pandas import DataFrame

#
# Generic filters
#
def filter_equal(df: DataFrame, attr_name: str, value):
	return getattr(df, attr_name) == value

#
# string
#
def filter_str_contains(df: DataFrame, attr_name: str, value: str):
	return getattr(df, attr_name).str.contains(value)
def filter_str_regex(df: DataFrame, attr_name: str, pattern: str):
	return getattr(df, attr_name).str.match(pattern)

#
# list
#
def filter_list_length(df: DataFrame, attr_name: str, length: int):
	return getattr(df, attr_name).str.len() == length
def filter_list_non_empty(df: DataFrame, attr_name: str):
	return getattr(df, attr_name).str.len() != 0

def filter_list_contains(df: DataFrame, attr_name: str, value):
	# https://stackoverflow.com/questions/41518920/python-pandas-how-to-query-if-a-list-type-column-contains-something
	return getattr(df, attr_name).str.contains(value, regex=False)

def filter_list_equal_at_index(df: DataFrame, attr_name: str, index: int, value):
	return getattr(df, attr_name).str[index] == value

#
# dict
#
filter_dict_length = filter_list_length
filter_dict_non_empty = filter_list_non_empty
filter_dict_contains_key = filter_list_contains
filter_dict_value_at_key = filter_list_equal_at_index


#
# Combining filters
#
def join_filters_with_and(*filters: DataFrame):
	if not filters:
		raise ValueError("No filters given")

	return reduce(and_, filters)
