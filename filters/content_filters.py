from pandas import DataFrame

from .base_filters import *
from ..parsing.description_details import	DescriptionDetailsParser_Friends, \
											DescriptionDetailsParser_Location
from ..parsing.consts import GROUP_SEPERATOR



def filter_main_group(df: DataFrame, main_group: str):
	return filter_equal(df, "main_group", main_group)
def filter_group_at_index(df: DataFrame, group: str, index: int):
	return filter_list_equal_at_index(df, "groups", index, group)
def filter_sub_groups(df: DataFrame, *sub_groups: str):
	return join_filters_with_and(
		filter_group_at_index(df, group, index)
		for index, group in enumerate(sub_groups)
	)
def filter_sub_groups_from_str(df: DataFrame, sub_groups: str):
	return filter_sub_groups(df, *sub_groups.split(GROUP_SEPERATOR))
def filter_sub_groups_at_any_index(df: DataFrame, sub_group: str):
	if sub_group.startswith(GROUP_SEPERATOR):
		sub_group = sub_group[len(GROUP_SEPERATOR):] 
	return filter_list_contains(df, "groups", sub_group)
def filter_num_groups(df: DataFrame, amount: int):
	return filter_list_length(df, "groups", amount)

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
def filter_friends_from_str(df: DataFrame, friends: str):
	friends: list = DescriptionDetailsParser_Friends.extract_values_from_string(friends)
	return join_filters_with_or(
		filter_friends_contain(df, friend)
		for friend in friends
	)

def filter_has_location(df: DataFrame):
	return filter_str_non_empty(df, "location")
def filter_location_exact(df: DataFrame, location: str):
	return filter_str_contains(df, "location", location)
def filter_location_from_str(df: DataFrame, location: str):
	location: str = DescriptionDetailsParser_Location.extract_values_from_string(location)
	return filter_location_exact(df, location)

def filter_has_vehicle(df: DataFrame):
	return filter_str_non_empty(df, "vehicle")
def filter_vehicle_exact(df: DataFrame, vehicle: str):
	return filter_str_contains(df, "vehicle", vehicle)

def filter_has_extra_details(df: DataFrame):
	return filter_dict_non_empty(df, "extra_details")
def filter_has_extra_details_key(df: DataFrame, key: str):
	return filter_dict_contains_key(df, "extra_details", key)
def filter_has_extra_details_value_exact(df: DataFrame, key: str, value: str):
	return filter_dict_value_in_key(df, "extra_details", key, value)

def filter_duration(df: DataFrame, duration: float, operation):
	return operation(df.total_seconds, duration)
def filter_duration_more_than(df: DataFrame, duration: float):
	return filter_duration(df, duration, operator.gt)
def filter_duration_less_than(df: DataFrame, duration: float):
	return filter_duration(df, duration, operator.lt)
def filter_duration_from_str(df: DataFrame, duration: str):
	if duration[0] == '>':
		return filter_duration_more_than(df, int(duration[1:]))
	if duration[0] == '<':
		return filter_duration_less_than(df, int(duration[1:]))
# File name
def filter_file_name_contains(df: DataFrame, file_name: str):
	return filter_str_contains(df, "_file_name", file_name)
def filter_file_name_exact(df: DataFrame, file_name: str):
	return filter_equal(df, "_file_name", file_name)

# Line
def filter_line_number(df: DataFrame, line: int):
	return filter_equal(df, "_line", line)
