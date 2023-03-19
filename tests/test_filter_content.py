from TimeCsv.tests.utils import *

from TimeCsv.filters.content_filters import *


def test_filter_main_group(df):
	assert len(
		df[filter_main_group(df, "Friends")]
	) == 1
	assert len(
		df[filter_main_group(df, "Sleep")]
	) == 2

def test_filter_group_at_index(df):
	assert len(
		df[filter_group_at_index(df, "Friends", 0)]
	) == 1
	assert len(
		df[filter_group_at_index(df, "Host", 1)]
	) == 1
	
def test_filter_sub_groups(df):
	assert len(
		df[filter_sub_groups(df, "Friends", "Host")]
	) == 1

def test_filter_sub_groups_from_str(df):
	assert len(
		df[filter_sub_groups_from_str(df, "Friends:Host")]
	) == 1

def test_filter_num_groups(df):
	assert len(
		df[filter_num_groups(df, 1)]
	) == 2
	assert len(
		df[filter_num_groups(df, 2)]
	) == 2
	
def test_filter_description_contains(df):
	assert len(
		df[filter_description_contains(df, "night")]
	) == 2

def test_filter_description_exact(df):
	assert len(
		df[filter_description_exact(df, "night")]
	) == 2

def test_filter_description_regex(df):
	assert len(
		df[filter_description_regex(df, "ho?[abcs]t")]
	) == 1

def test_filter_has_friends(df):
	assert len(
		df[filter_has_friends(df)]
	) == 1

def test_filter_friends_contain(df):
	assert len(
		df[filter_friends_contain(df, "FriendA")]
	) == 1

def test_filter_friends_from_str(df):
	assert len(
		df[filter_friends_from_str(df, "with FriendA")]
	) == 1

def test_filter_has_location(df):
	assert len(
		df[filter_has_location(df)]
	) == 1

def test_filter_location_exact(df):
	assert len(
		df[filter_location_exact(df, "home")]
	) == 1

def test_filter_has_vehicle(df):
	assert len(
		df[filter_has_vehicle(df)]
	) == 0

def test_filter_vehicle_exact(df):
	assert len(
		df[filter_vehicle_exact(df, "Car")]
	) == 0

def test_filter_has_extra_details(df):
	assert len(
		df[filter_has_extra_details(df)]
	) == 1

def test_filter_has_extra_details_key(df):
	assert len(
		df[filter_has_extra_details_key(df, "some_game")]
	) == 1

def test_filter_duration_more_than(df):
	assert len(
		df[filter_duration_more_than(df, 1.5*60*60)]
	) == 2

def test_filter_duration_less_than(df):
	assert len(
		df[filter_duration_less_than(df, 50*60)]
	) == 1

def test_filter_duration_from_str(df):
	assert len(
		df[filter_duration_from_str(df, ">1801")] # 1.5*60*60=1.5hour
	) == 3

def test_filter_file_name_contains(df):
	assert len(
		df[filter_file_name_contains(df, "fake_data")]
	) == NUM_ENTRIES

def test_filter_file_name_exact(df):
	assert len(
		df[filter_file_name_exact(df, FAKE_DATA_PATH)]
	) == NUM_ENTRIES

def test_filter_line_number(df):
	assert len(
		df[filter_line_number(df, 2)]
	) == 1
