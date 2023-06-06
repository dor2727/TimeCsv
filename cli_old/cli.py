import argparse

from ..utils.consts import DEFAULT_DATA_DIRECTORY


# may pass arguments as a list (used in the telegram bot)
def parse_args(args_list=None):
	parser = argparse.ArgumentParser()
	parser.add_argument("--file", "--folder", "-f", type=str, default=DEFAULT_DATA_DIRECTORY, dest="file", help="which file/folder to read")

	# filter time
	time = parser.add_argument_group("Time")
	time.add_argument("--days-back", "-d", type=int , default=None, dest="days_back"   , help="how many days back to query (0 for today only, 1 includes yesterday, etc.)")
	time.add_argument("--months-back"    , type=int , default=None, dest="months_back" , help="how many month summaries to show")
	time.add_argument("--month"    , "-m", type=str , default=None, dest="month"       , help="which month to query. can be comma seperated (e.g. 1,2,3,9)")
	time.add_argument("--year"     , "-y", type=str , default=None, dest="year"        , help="which year to query. can be comma seperated (e.g. 2019,2020)")
	time.add_argument("--all-time"       , action="store_true"    , dest="all_time"    , help="whether to all the time")
	time.add_argument("--time-use-and"   , action="store_true"    , dest="time_use_and", help="whether to use AND or OR when adding the filters (default - OR)")

	# filter
	search = parser.add_argument_group("Search")
	search.add_argument("search_string", type=str, nargs=argparse.REMAINDER)
	search_advanced = parser.add_argument_group("Advanced search")
	search_advanced.add_argument("--search-use-or", action="store_true", dest="search_use_or", help="whether to use AND or OR when adding the filters. Default: AND")

	# set group
	grouping = parser.add_argument_group("grouping")
	grouping.add_argument("--group-by", type=str.lower, default="main_group", dest="group_by", help="Group events by some category")
	grouping.add_argument("--list-group-by-options", action="store_true", dest="list_group_by_options", help="List the categories for --group-by")

	debug = parser.add_argument_group("debug")
	debug.add_argument("--verbose", "-v", action="store_true", dest="verbose", help="verbosity")


	if args_list is None:
		args = parser.parse_args()
	else:
		args = parser.parse_args(args_list)

	return post_process_args(args)

def post_process_args(args: argparse.Namespace):
	if args.verbose:
		print(args)

	return args
