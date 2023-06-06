import argparse
from pandas import DataFrame

from ..filters import	join_filters_with_or, join_filters_with_and, \
						filter_days_back, filter_month, filter_year
from ..filters.time_filters import _get_today

def _iterate_months_back(n: int) -> "Iterable[int]":
	current_month = _get_today().month
	for index in range(n):
		month = current_month - index
		if month < 1:
			month += 12
		yield month

def _create_default_time_filter(df: DataFrame):
	filters = []
	for month in _iterate_months_back(2):
		filters.append(
			filter_month(df, month)
		)
	return join_filters_with_or(filters)

def filter_by_time(df, args: argparse.Namespace):
	if args.all_time:
		return df

	filters = []

	if args.time_use_and:
		combine = join_filters_with_and
	else:
		combine = join_filters_with_or

	if args.days_back is not None:
		filters.append(
			filter_days_back(df, args.days_back)
		)

	if args.months_back is not None:
		for month in _iterate_months_back(args.months_back):
			filters.append(
				filter_month(df, month)
			)

	if args.month is not None:
		months = map(int, args.month.split(','))
		for month in months:
			filters.append(
				filter_month(df, month)
			)

	if args.year is not None:
		years = map(int, args.year.split(','))
		for year in years:
			filters.append(
				filter_year(df, year)
			)

	if filters:
		df_filter = combine(filters)
	else:
		df_filter = _create_default_time_filter(df)

	return df[df_filter]
