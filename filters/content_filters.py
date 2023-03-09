from pandas import DataFrame

from .base_filters import *


def filter_main_group(df: DataFrame, main_group: str):
	return filter_equal(df, "main_group", main_group)
def filter_group_at_index(df: DataFrame, group: str, index: int):
	return filter_list_equal_at_index(df, "groups", index, group)
def filter_sub_groups(df: DataFrame, *sub_groups: str):
	return join_filters_with_and(
		filter_group_at_index(df, group, index)
		for index, group in enumerate(sub_groups)
	)
def filter_num_groups(df: DataFrame, amount: int):
	return filter_list_length(df, "groups", amount)

# Description
def filter_description_contains(df: DataFrame, description: str):
	return filter_str_contains(df, "description", description)
def filter_description_exact(df: DataFrame, description: str):
	return filter_equal(df, "description", description)
def filter_description_regex(df: DataFrame, description: str):
	return filter_str_regex(df, "description", description)

def filter_has_friends(df: DataFrame):
	return filter_list_non_empty(df, "friends")
def filter_friends_contain(df: DataFrame, friend: str):
	return filter_list_contains(df, "friends", friend)

def filter_has_extra_details(df: DataFrame):
	return filter_dict_non_empty(df, "extra_details")
def filter_has_extra_details_key(df: DataFrame, key: str):
	return filter_dict_contains_key(df, "extra_details", key)

# File name
def filter_file_name_contains(df: DataFrame, file_name: str):
	return filter_str_contains(df, "_file_name", file_name)
def filter_file_name_exact(df: DataFrame, file_name: str):
	return filter_equal(df, "_file_name", file_name)

# Line
def filter_line_number(df: DataFrame, line: int):
	return filter_equal(df, "_line", line)

