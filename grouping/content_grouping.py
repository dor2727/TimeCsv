from .base_grouping import *
from ..filters import filter_sub_groups, filter_has_extra_details_key


def get_all_main_group(df: DataFrame):
	return get_unique_values(df, "main_group")

def get_all_sub_groups(df: DataFrame, *groups: str):
	filtered_df = df[filter_sub_groups(df, *groups)]
	next_subgroup_index = len(groups)
	return get_unique_values_at_index(filtered_df, "groups", next_subgroup_index)

def get_all_sub_groups_at_index(df: DataFrame, index: int):
	return get_unique_values_at_index(df, "groups", index)

def get_all_description(df: DataFrame):
	return get_unique_values(df, "description")

def get_all_extra_details_keys(df: DataFrame):
	return union_of_df_of_iterables(df.extra_details)

def get_all_extra_details_values(df: DataFrame, key: str):
	filtered_df = df[filter_has_extra_details_key(df, key)]
	all_values = filtered_df.extra_details.str[key]
	return union_of_df_of_iterables(all_values)

def get_all_friends(df: DataFrame):
	return union_of_df_of_iterables(df.friends)

def get_all_locations(df: DataFrame):
	return get_unique_values(df, "location")

def get_all_vehicles(df: DataFrame):
	return get_unique_values(df, "vehicle")
