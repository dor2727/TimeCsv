import os

import TimeCsv.statistics
from TimeCsv.utils import print_items
from TimeCsv.parsing import DataFolder, DataFile
from TimeCsv.cli.filters import initialize_time_filter, initialize_search_filter

# Find the relative file path (it may be a relative path)
def open_data_file(data_object=None, file_path=None):
	# this will mostly happen when called from the telegram bot,
	# 	which already uses a DataFolder
	if data_object:
		return data_object

	if not file_path:
		raise ValueError(f"file/folder not given")

	file_path = os.path.expanduser(file_path)

	if os.path.exists(file_path):
		if os.path.isfile(file_path):
			return DataFile(file_path)
		if os.path.isdir(file_path):
			return DataFolder(file_path)

	# try relative path:
	elif os.path.exists(rel_path := os.path.join(os.getcwd(), file_path)):
		if os.path.isfile(rel_path):
			return DataFile(rel_path)
		if os.path.isdir(rel_path):
			return DataFolder(rel_path)

	# try a path relative to the default directory:
	elif os.path.exists(rel_path := os.path.join(DEFAULT_DATA_DIRECTORY, file_path)):
		if os.path.isfile(rel_path):
			return DataFile(rel_path)
		if os.path.isdir(rel_path):
			return DataFolder(rel_path)

	raise ValueError(f"file/folder not found: {file_path}")

# use the filters & the data_object to filter out the relevant data
def get_data(data_object, args):
	# initialize filters
	time_filter   = initialize_time_filter(args)
	search_filter = initialize_search_filter(args)

	
	# filter data by time
	if time_filter is None:
		data          = data_object.data
		selected_time = "All time"
	else:
		data          = time_filter % data_object.data
		selected_time = time_filter.get_selected_time()

	return data, selected_time, search_filter


# telegram helper - return the data in one of the following formats, according to args:
# 	pie, bar, telegram, text
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
			result = ''
		elif args.bar:
			g.to_bar(save=False)
			result = ''
		else:
			result = g.to_text()

		if args.show_items:
			result += "\n------\n"
			result += print_items(g.data, ret=True)

		return result


# handles the 'special' category of the args, or the default
def get_special_text(data, selected_time, args):
	groupedstats_params = {
		"selected_time" : selected_time,
		"group_value"   : args.grouping_method,
		"sort"          : args.sorting_method,
	}
	kwargs = {}

	# big switch-case for different GroupedStats classes
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

	return get_text(g, args)

# handles search_filter
def get_search_filter_text(data, selected_time, search_filter, args):
	found_items = search_filter % data

	g = TimeCsv.statistics.FilteredStats(
		found_items,
		selected_time=selected_time
	)

	return get_text(g, args)
