from pandas import DataFrame
from argparse import Namespace
import datetime

from ..filters import (
	join_filters_with_and, join_filters_with_or,
	filter_days_back, filter_month, filter_year
)

def filter_df_by_time(df: DataFrame, args: Namespace):
	if args.all_time:
		return df

	set_default_time_filter_arguments_if_needed(args)

	joined_filters = prepare_filters(df, args)

	if joined_filters is None:
		import ipdb; ipdb.set_trace()
		return df
	else:
		return df[joined_filters]

def set_default_time_filter_arguments_if_needed(args: Namespace):
	if (
		(args.days_back is None)
		and (args.months_back is None)
		and (args.month is None)
		and (args.year is None)
		and (args.all_time is False)
	):
		args.months_back = 2

def prepare_filters(df: DataFrame, args: Namespace):
	filters = []

	if args.days_back is not None:
		filters.append(filter_days_back(df, args.days_back))

	if args.month is not None:
		month_filters = [
			filter_month(df, m)
			for m in map(int, args.month.split(','))
		]
		filters.append(join_filters_with_or(month_filters))

	if args.year is not None:
		year_filters = [
			filter_year(df, y)
			for y in map(int, args.year.split(','))
		]
		filters.append(join_filters_with_or(year_filters))
		
	if args.months_back is not None:
		current_month = datetime.datetime.now().month

		months_back_filters = []

		for i in range(args.months_back):
			m = ((current_month - 1 - i)  % 12) + 1
			months_back_filters.append(filter_month(df, m))

		filters.append(join_filters_with_or(months_back_filters))


	if not filters:
		f = None
	elif args.time_use_and:
		f = join_filters_with_and(filters)
	else:
		f = join_filters_with_or(filters)

	if args.debug:
		print(f"[*] time filter: {f}")

	return f
