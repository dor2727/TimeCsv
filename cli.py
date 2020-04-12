#!/usr/bin/rlwrap python3

import os
import sys
import argparse
import datetime

import TimeCsv.statistics
from TimeCsv.parsing import DataFolder
from TimeCsv.time_utils import newest
from TimeCsv.filters import *



def parse_args():
	parser = argparse.ArgumentParser()

	search = parser.add_argument_group("search")
	search.add_argument("search_string"     , type=str , default=''  , nargs=argparse.REMAINDER)
	search.add_argument("--search-use-or"   , action="store_true"    , dest='search_use_or', help='whether to use AND or OR when adding the filters')
	search.add_argument("--show-items", "-s", action="store_true"    , dest='show_items'   , help='whether to print all the items')

	time = parser.add_argument_group("time")
	time.add_argument("--days-back", "-d", type=int , default=None, dest='days_back'   , help="how many days back to query")
	time.add_argument("--month-back"     , type=int , default=None, dest='months_back' , help='how many month summaries to show')
	time.add_argument("--month"    , "-m", type=str , default=None, dest='month'       , help='which month to query. can be comma seperated (e.g. 1,2,3,9)')
	time.add_argument("--year"     , "-y", type=str , default=None, dest='year'        , help='which year to query. can be comma seperated (e.g. 2019,2020)')
	time.add_argument("--all-time"       , action="store_true"    , dest='all_time'    , help='whether to all the time')
	time.add_argument("--time-use-and"   , action="store_true"    , dest='time_use_and', help='whether to use AND or OR when adding the filters')


	debugging = parser.add_argument_group("debugging")
	debugging.add_argument("--debug"          , action="store_true")
	debugging.add_argument("--test"           , action="store_true")

	args = parser.parse_args()

	if args.debug:
		print(f"[*] args: {args}")

	return args

def build_time_filter(args):
	filters = []

	if args.days_back is not None:
		filters.append(TimeFilter_Days(args.days_back))

	if args.month is not None:
		month_filters = [
			TimeFilter_Month(int(m))
			for m in args.month.split(',')
		]
		filters.append(join_filters_with_or(month_filters))

	if args.year is not None:
		year_filters = [
			TimeFilter_Year(int(y))
			for y in args.year.split(',')
		]
		filters.append(join_filters_with_or(year_filters))
		
	if args.months_back is not None:
		current_month = datetime.datetime.now().month

		months_back_filters = []

		for i in range(args.months_back):
			m = ((current_month - 1 - i)  % 12) + 1
			months_back_filters.append(TimeFilter_Month(int(m)))

		filters.append(join_filters_with_or(months_back_filters))


	if args.time_use_and:
		f = join_filters_with_and(filters)
	else:
		f = join_filters_with_or(filters)

	if args.debug:
		print(f"[*] time filter: {f}")

	return f

def initialize_time_filter(args):
	if args.all_time:
		return None

	time_filter   = build_time_filter(args)

	if time_filter is None:
		args.months_back = 2
		time_filter = build_time_filter(args)

	return time_filter

def initialize_search_filter(args):
	filters = []

	for s in args.search_string:
		filters.append(AutoFilter(s))

	if args.search_use_or:
		f = join_filters_with_or(filters)
	else:
		f = join_filters_with_and(filters)

	if args.debug:
		print(f"[*] search filter: {f}")

	return f


def main():
	args = parse_args()

	if args.test:
		test(debug=args.debug)
		return


	# initialize filters
	time_filter   = initialize_time_filter(args)
	search_filter = initialize_search_filter(args)

	# initialize data
	d = DataFolder()

	# filter data by time
	if time_filter is None:
		data = d.data
		selected_time = "All time"
	else:
		data = time_filter % d.data
		selected_time = time_filter.get_selected_time()

	"""
	if search_filter:
		filter data by the search_filter
		and show FilteredStats
	else:
		print GroupedStats_Group
	"""
	if search_filter is None:
		# default statistics
		g = TimeCsv.statistics.GroupedStats_Group(
			data,
			selected_time=selected_time,
			group_value="time"
		)
		print(g.to_text())
	else:
		found_items = search_filter % data

		print(TimeCsv.statistics.FilteredStats(
			found_items,
			selected_time=selected_time
		).to_text())

		if args.show_items:
			print("------")
			print_items(found_items)

def test(debug=False):
	print("[*] test")

	b = DataFolder("/home/me/Dropbox/Projects/Time/data")
	if debug:
		print(f"DataFolder: {b}")

	f = TimeFilter_Month(3) | TimeFilter_Month(4)
	f_data = f.get_filtered_data(b.data)
	print(len(f_data))

	g = TimeCsv.statistics.GroupedStats_Games(f_data, group_value="amount")
	# g = TimeCsv.statistics.GroupedStats_Youtube(f_data, group_value="time")
	# g = TimeCsv.statistics.GroupGroupedStats(f_data, group_value="time", category_name="Youtube")
	print(g.group())
	print(g.to_text())
	# print(g.to_pie(save=False))

	import pdb; pdb.set_trace()

