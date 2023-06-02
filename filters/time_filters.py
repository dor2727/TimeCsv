from pandas import DataFrame
from datetime import datetime, timedelta

from .base_filters import *
from ..utils.consts import WEEK_STARTS_AT_SUNDAY
from ..utils.times import Days


def _get_today() -> datetime:
	now = datetime.now()
	return datetime(now.year, now.month, now.day)
def _get_last_week_start() -> datetime:
	today = _get_today()

	distance_to_week_start: Days = today.weekday() + WEEK_STARTS_AT_SUNDAY
	distance_to_week_start %= 7

	return today - timedelta(days=distance_to_week_start)
def _get_last_week_end() -> datetime:
	return _get_last_week_start() - timedelta(days=1)
def _find_latest_year(month: int):
	assert 1 <= month <= 12
	today = _get_today()
	current_month = today.month
	current_year = today.year

	if month <= current_month:
		return current_year
	else:
		return current_year - 1

def filter_date(df: DataFrame, value: datetime, operation):
	return operation(df.date, value)
def filter_date_after_and_including(df: DataFrame, value: datetime):
	return df.date >= value
def filter_date_between(df: DataFrame, lower_value: datetime, upper_value: datetime):
	return (lower_value <= df.date) & (df.date <= upper_value)

def filter_days_back(df: DataFrame, n: int=0):
	"n=0 means today, n=1 means tomorrow plus today"
	n = abs(n)
	previous_n_days = _get_today() - timedelta(days=n)
	return filter_date_after_and_including(df, previous_n_days)
def filter_today(df: DataFrame):
	return filter_days_back(df, 0)
def filter_yesterday(df: DataFrame):
	return filter_days_back(df, 1)
def filter_yesterday_only(df: DataFrame):
	yesterday = _get_today() - timedelta(days=1)
	return filter_date_between(df, yesterday, yesterday)
def filter_this_week(df: DataFrame):
	"from the start of the week until today, including both"
	return filter_date_after_and_including(df, _get_last_week_start())
def filter_previous_week(df: DataFrame):
	"from the previous start of the week until the last end of the week, including both"
	previous_week_start = _get_last_week_start() - timedelta(days=7)
	previous_week_end   = _get_last_week_end()
	return filter_date_between(df, previous_week_start, previous_week_end)

def filter_year(df: DataFrame, year: int):
	return df.date.dt.year == year
def filter_this_year(df: DataFrame):
	return filter_year(df, _get_today().year)

def filter_month(df: DataFrame, month: int, year: int=None):
	if year is None:
		year = _find_latest_year(month)

	return (df.date.dt.month == month) & (df.date.dt.year == year)
def filter_this_month(df: DataFrame):
	today = _get_today()
	return filter_month(df, today.month, today.year)
