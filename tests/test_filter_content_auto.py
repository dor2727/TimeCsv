from TimeCsv.tests.utils import *

from TimeCsv.filters.content_filters import *
from TimeCsv.filters.auto_content_filter import *

def test_filter_content_auto__duration(df):
	assert (
		filter_content_auto(df, ">3601") == filter_duration_more_than(df, 3601)
	).all()
	assert (
		filter_content_auto(df, "<3601") == filter_duration_less_than(df, 3601)
	).all()

def test_filter_content_auto__friends(df):
	assert (
		filter_content_auto(df, "with FriendA") == filter_friends_contain(df, "FriendA")
	).all()

def test_filter_content_auto__location(df):
	assert (
		filter_content_auto(df, "@home@") == filter_location_exact(df, "home")
	).all()

def test_filter_content_auto__description(df):
	assert (
		filter_content_auto(df, "night") == filter_description_contains(df, "night")
	).all()

def test_filter_content_auto__sub_groups(df):
	assert (
		filter_content_auto(df, "Gaming:Console") == filter_sub_groups(df, "Gaming", "Console")
	).all()

def test_filter_content_auto__main_group(df):
	assert (
		filter_content_auto(df, "Gaming") == filter_main_group(df, "Gaming")
	).all()

def test_filter_content_auto__default(df):
	assert (
		filter_content_auto(df, "gamING") == filter_main_group(df, "Gaming")
	).all()
	assert (
		filter_content_auto(df, "nIGHT") == filter_description_contains(df, "night")
	).all()
