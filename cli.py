#!/usr/bin/rlwrap python3

import os
import sys
import argparse
import datetime

import TimeCsv.statistics
from TimeCsv.parsing import DataFolder, DataFile, ParseError
from TimeCsv.time_utils import newest
from TimeCsv.filters import *
from TimeCsv.functions.productivity import get_productivity_pie



# may pass arguments as a list (used in the telegram bot)
def parse_args(args_list=None):
	parser = argparse.ArgumentParser()
	parser.add_argument("--file", "--folder", "-f", type=str, default=DEFAULT_DATA_DIRECTORY, dest="file", help="which file/folder to read")

	search = parser.add_argument_group("search")
	search.add_argument("search_string"        , type=str, default=''        , nargs=argparse.REMAINDER)
	search.add_argument("--group-by"           , type=str, default="time"    , dest="grouping_method", help="grouping method (time or time_average/avg or amount)")
	search.add_argument("--sort"               , type=str, default="by_value", dest="sorting_method" , help="sorting method (by_value/value or alphabetically/abc)")
	search.add_argument("--search-use-or"      , action="store_true"         , dest="search_use_or"  , help="whether to use AND or OR when adding the filters")
	search.add_argument("--show-items", "-s"   , action="store_true"         , dest="show_items"     , help="whether to print all the items")
	search.add_argument("--force-regex", "--re", action="store_true"         , dest="force_regex"    , help="whether to use regex in all search terms")

	time = parser.add_argument_group("time")
	time.add_argument("--days-back", "-d", type=int , default=None, dest="days_back"   , help="how many days back to query")
	time.add_argument("--months-back"    , type=int , default=None, dest="months_back" , help="how many month summaries to show")
	time.add_argument("--month"    , "-m", type=str , default=None, dest="month"       , help="which month to query. can be comma seperated (e.g. 1,2,3,9)")
	time.add_argument("--year"     , "-y", type=str , default=None, dest="year"        , help="which year to query. can be comma seperated (e.g. 2019,2020)")
	time.add_argument("--all-time"       , action="store_true"    , dest="all_time"    , help="whether to all the time")
	time.add_argument("--time-use-and"   , action="store_true"    , dest="time_use_and", help="whether to use AND or OR when adding the filters")


	debugging = parser.add_argument_group("debugging")
	debugging.add_argument("--debug"   , action="store_true")
	debugging.add_argument("--test"    , action="store_true")

	grouping = parser.add_argument_group("grouping")
	grouping.add_argument("--group"              , type=str , default=None, dest="group"       , help="show statistics per group")
	grouping.add_argument("--friend", "--friends", action="store_true"    , dest="friend"      , help="show friend statistics")
	grouping.add_argument("--location"           , action="store_true"    , dest="location"    , help="show location statistics")
	#
	grouping.add_argument("--youtube"            , action="store_true"    , dest="youtube"     , help="show youtube statistics")
	grouping.add_argument("--gaming"             , action="store_true"    , dest="gaming"      , help="show gaming statistics")

	details = parser.add_argument_group("details")
	details.add_argument("--extra-details", "--extra", action="store_true", dest="extra_details", help="extra details within the search filter")
	details.add_argument("--lecture"                 , action="store_true", dest="lecture"      , help="show lecture statistics")
	details.add_argument("--homework"                , action="store_true", dest="homework"     , help="show homework statistics")
	details.add_argument("--shower"                  , action="store_true", dest="shower"       , help="show shower statistics")
	details.add_argument("--prepare-food"            , action="store_true", dest="prepare_food" , help="show cooking statistics")

	output = parser.add_argument_group("output")
	output.add_argument("--telegram", action="store_true")
	output.add_argument("--pie"     , action="store_true")
	output.add_argument("--bar"     , action="store_true")

	details.add_argument("--productive-pie"        , action="store_true", dest="productive_pie"        , help="whether to show a productive_pie")
	details.add_argument("--productive-pie-focused", action="store_true", dest="productive_pie_focused", help="whether to focus the productive_pie")


	if args_list is None:
		args = parser.parse_args()
	else:
		args = parser.parse_args(args_list)

	if args.debug:
		print(f"[*] args: {args}")

	expand_args(args)

	return args

def expand_args(args):
	if args.sorting_method == "abc":
		args.sorting_method = "alphabetically"
	if args.sorting_method == "value":
		args.sorting_method = "by_value"

	if args.grouping_method == "avg":
		args.grouping_method = "time_average"

	if args.gaming:
		args.group = "Gaming"
	elif args.youtube:
		args.group = "Youtube"

	if args.extra_details:
		args.force_regex = True



#
# time filters
#
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

	# if nothing is set, use default value
	if time_filter is None:
		# if the default location is used, set the filter to 2 months
		if args.file == DEFAULT_DATA_DIRECTORY:
			args.months_back = 2
			time_filter = build_time_filter(args)
		# else, treat it as `all_time`
		else:
			return None

	return time_filter

def initialize_search_filter(args):
	filters = []

	for s in args.search_string:
		filters.append(AutoFilter(s, force_regex=args.force_regex))

	if args.search_use_or:
		f = join_filters_with_or(filters)
	else:
		f = join_filters_with_and(filters)

	if args.debug:
		print(f"[*] search filter: {f}")

	return f


#
# data retrival
#

# use the filters & the data_object to filter out the relevant data
def get_data(data_object, args):
	# initialize filters
	time_filter   = initialize_time_filter(args)
	search_filter = initialize_search_filter(args)

	
	# filter data by time
	if time_filter is None:
		data = data_object.data
		selected_time = "All time"
	else:
		data          = time_filter % data_object.data
		selected_time = time_filter.get_selected_time()

	return data, selected_time, search_filter


# telegram helper
def get_text(g, args):
	if args.telegram:
		if args.pie:
			return g.to_pie(save=True)
		elif args.bar:
			return g.to_bar(save=True)
		else:
			return g.to_telegram()

	else:
		if args.pie:
			g.to_pie(save=False)
			return ''
		elif args.bar:
			g.to_bar(save=False)
			return ''
		else:
			return g.to_text()


# handles the 'special' category of the args, or the default
def get_special_text(data, selected_time, args):
	groupedstats_params = {
		"selected_time" : selected_time,
		"group_value"   : args.grouping_method,
		"sort"          : args.sorting_method,
	}
	# big switch-case for different GroupedStats classes
	kwargs = {}
	if args.location:
		cls = TimeCsv.statistics.GroupedStats_Location
	elif args.friend:
		cls = TimeCsv.statistics.GroupedStats_Friend
	elif args.group:
		cls = TimeCsv.statistics.GroupGroupedStats
		kwargs = {"category_name": args.group.capitalize()}
	elif args.lecture:
		cls = TimeCsv.statistics.GroupedStats_Lecture
	elif args.homework:
		cls = TimeCsv.statistics.GroupedStats_Homework
	elif args.shower:
		cls = TimeCsv.statistics.GroupedStats_Shower
	elif args.prepare_food:
		cls = TimeCsv.statistics.GroupedStats_PrepareFood
	else: # default statistics
		cls = TimeCsv.statistics.GroupedStats_Group


	g = cls(
		data,
		**kwargs,
		**groupedstats_params
	)

	return get_text(g, args)

# handles the 'extra-details' flag
def get_extra_details_text(data, selected_time, search_filter, args):
	groupedstats_params = {
		"selected_time" : selected_time,
		"group_value"   : args.grouping_method,
		"sort"          : args.sorting_method,
	}

	g = TimeCsv.statistics.GroupedStats_ExtraDetailGeneric(
		search_filter,
		data,
		**groupedstats_params,
	)

	result = get_text(g, args)

	if args.show_items:
		result += "\n------\n"
		result += print_items(g.data, ret=True)

	return result


# handles search_filter
def get_search_filter_text(data, selected_time, search_filter, args):
	found_items = search_filter % data

	g = TimeCsv.statistics.FilteredStats(
		found_items,
		selected_time=selected_time
	)
	result = get_text(g, args)

	if args.show_items:
		result += "\n------\n"
		result += print_items(found_items, ret=True)

	return result


#
# file utils
#
def open_data_file(data_object=None, file_path=None):
	# this will mostly happen when called from the telegram bot,
	# 	which already uses a DataFolder
	if data_object:
		return data_object

	if not file_path:
		raise ValueError(f"file/folder not found: {file_path}")

	file_path = os.path.expanduser(file_path)

	if os.path.exists(file_path):
		if os.path.isfile(file_path):
			return DataFile(file_path)
		if os.path.isdir(file_path):
			return DataFolder(file_path)

	# try relative path:
	elif os.path.exists(os.path.join(os.getcwd(), file_path)):
		file_path = os.path.join(os.getcwd(), file_path)
		if os.path.isfile(file_path):
			return DataFile(file_path)
		if os.path.isdir(file_path):
			return DataFolder(file_path)

	# try a path relative to the default directory:
	elif os.path.exists(os.path.join(DEFAULT_DATA_DIRECTORY, file_path)):
		file_path = os.path.join(DEFAULT_DATA_DIRECTORY, file_path)
		if os.path.isfile(file_path):
			return DataFile(file_path)

	raise ValueError(f"file/folder not found: {file_path}")


def main(data_object=None, args_list=None):
	args = parse_args(args_list=args_list)

	if args.test:
		test(debug=args.debug)
		return

	data_object = open_data_file(data_object, args.file)

	data, selected_time, search_filter = get_data(data_object, args)

	if args.productive_pie:
		return get_productivity_pie(data, selected_time, save=False, focused=args.productive_pie_focused)
	elif search_filter is None:
		return get_special_text(data, selected_time, args)
	elif search_filter is not None and args.extra_details:
		return get_extra_details_text(data, selected_time, search_filter, args)
	else:
		return get_search_filter_text(data, selected_time, search_filter, args)

def test(debug=False):
	print("[*] test")

	try:
		b = DataFolder()
	except ParseError as pe:
		print("ParseError")
		import pdb; pdb.set_trace()
		print("ParseError")
	except Exception as exc:
		print("Exception")
		import pdb; pdb.set_trace()
		print("Exception")

	if debug:
		print(f"DataFolder: {b}")


	f = TimeFilter_Month(3) | TimeFilter_Month(4)
	# f = TimeFilter_Month(3) | TimeFilter_Month(4) | TimeFilter_Month()
	# f = TimeFilter_Days(7)
	# f = TimeFilter_Days(1)
	f_data = f.get_filtered_data(b.data)
	print(len(f_data))


	g = TimeCsv.statistics.GroupedStats_Games(f_data, group_value="amount")
	# g = TimeCsv.statistics.GroupedStats_Location(f_data)
	# g = TimeCsv.statistics.GroupedStats_Youtube(f_data, group_value="time")
	# g = TimeCsv.statistics.GroupGroupedStats(f_data, group_value="time", category_name="Youtube")
	print(g.group())
	print(g.to_text())
	print(g.to_bar())
	# print(g.to_pie(save=False))

	import pdb; pdb.set_trace()

