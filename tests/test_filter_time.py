from TimeCsv.tests.utils import *

from TimeCsv.filters.time_filters import *

import operator

from unittest import mock
import TimeCsv
from datetime import datetime

THE_NEW_TODAY = datetime(2021, 3, 4)

@pytest.fixture(scope="module", autouse=True)
def set_today():
	patch_obj = mock.patch.object(
		TimeCsv.filters.time_filters,
		"_get_today",
		return_value=THE_NEW_TODAY
	)
	with patch_obj:
		yield

def test_mock():
	assert TimeCsv.filters.time_filters._get_today() == THE_NEW_TODAY

def test_filter_date(df):
	assert len(
		df[filter_date(df, datetime(2021,1,1), operator.ge)]
	) == 3
def test_filter_date_after_and_including(df):
	assert len(
		df[filter_date_after_and_including(df, datetime(2021,1,1))]
	) == 3
def test_filter_date_between(df):
	assert len(
		df[filter_date_between(df, datetime(2021,1,1), datetime(2021,3,1))]
	) == 2
def test_filter_days_back(df):
	assert len(
		df[filter_days_back(df, 0)]
	) == 1
def test_filter_today(df):
	assert len(
		df[filter_today(df)]
	) == 1
def test_filter_yesterday(df):
	assert len(
		df[filter_yesterday(df)]
	) == 1
def test_filter_yesterday_only(df):
	assert len(
		df[filter_yesterday_only(df)]
	) == 0
def test_filter_this_week(df):
	assert len(
		df[filter_this_week(df)]
	) == 1
def test_filter_previous_week(df):
	assert len(
		df[filter_previous_week(df)]
	) == 0
def test_filter_year(df):
	assert len(
		df[filter_year(df, 2020)]
	) == 1
def test_filter_this_year(df):
	assert len(
		df[filter_this_year(df)]
	) == 3
def test_filter_month(df):
	assert len(
		df[filter_month(df, 2)]
	) == 2
	assert len(
		df[filter_month(df, 1, 2020)]
	) == 1
def test_filter_this_month(df):
	assert len(
		df[filter_this_month(df)]
	) == 1
