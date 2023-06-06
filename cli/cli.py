import argparse

from ..utils.consts import DEFAULT_DATA_DIRECTORY
from ..tree.sorting import SortingMethods

# may pass arguments as a list (used in the telegram bot)
def parse_args(args_list=None):
	parser = argparse.ArgumentParser()
	parser.add_argument("--file", "--folder", "-f", type=str, default=DEFAULT_DATA_DIRECTORY, dest="file", help="which file/folder to read")

	# filter time
	time = parser.add_argument_group("Time")
	# time.add_argument("--days-back", "-d", type=int , default=None, dest="days_back"   , help="how many days back to query (0 for today only, 1 includes yesterday, etc.)")
	# time.add_argument("--months-back"    , type=int , default=None, dest="months_back" , help="how many month summaries to show")
	# time.add_argument("--month"    , "-m", type=str , default=None, dest="month"       , help="which month to query. can be comma seperated (e.g. 1,2,3,9)")
	# time.add_argument("--year"     , "-y", type=str , default=None, dest="year"        , help="which year to query. can be comma seperated (e.g. 2019,2020)")
	# time.add_argument("--all-time"       , action="store_true"    , dest="all_time"    , help="whether to all the time")
	# time.add_argument("--time-use-and"   , action="store_true"    , dest="time_use_and", help="whether to use AND or OR when adding the filters (default - OR)")

	# # filter content
	# search = parser.add_argument_group("Search")
	# search.add_argument("search_string", type=str, nargs=argparse.REMAINDER)
	# search_advanced = parser.add_argument_group("Advanced search")
	# search_advanced.add_argument("--search-use-or", action="store_true", dest="search_use_or", help="whether to use AND or OR when adding the filters. Default: AND")

	# Tree level
	sorting = parser.add_argument_group("Tree level")
	sorting.add_argument("--max-hirarchy"        , type=str.lower, default="0", dest="max_hirarchy"            , help="How deep to show in the tree hirarchy")
	sorting.add_argument("--max-main", "--max-main-group", action="store_true", dest="max_main_group"          , help="short for `--max-hirarchy=0`")
	sorting.add_argument("--max-sub-group"       , type=int                   , dest="max_sub_group"           , help="short for `--max-hirarchy=int`")
	sorting.add_argument("--max-description"             , action="store_true", dest="max_description"         , help="short for `--max-hirarchy=description`")
	sorting.add_argument("--max-extra-details-keys"      , action="store_true", dest="max_extra_details_keys"  , help="short for `--max-hirarchy=extra_details_keys`")
	sorting.add_argument("--max-extra-details-values"    , action="store_true", dest="max_extra_details_values", help="short for `--max-hirarchy=extra_details_values`")

	# Sorting
	sorting = parser.add_argument_group("sorting")
	sorting.add_argument("--sort_method", type=SortingMethods.__getitem__, default="total_time", dest="sort_method", help="How to sort titles")
	sorting.add_argument("--alphabetical", "--abc", action="store_true", dest="alphabetical", help="short for `--sort-method=alphabetical`")
	sorting.add_argument("--total_time", "--time", action="store_true", dest="total_time", help="short for `--sort-method=total_time`")

	# Output
	output = parser.add_argument_group("output")
	output.add_argument("--pie", action="store_true", dest="pie", help="output result as a pie chart")

	debug = parser.add_argument_group("debug")
	debug.add_argument("--debug"        , action="store_true", dest="debug"  , help="debug")
	debug.add_argument("--verbose", "-v", action="store_true", dest="verbose", help="verbosity")


	if args_list is None:
		args = parser.parse_args()
	else:
		args = parser.parse_args(args_list)

	return post_process_args(args)

def post_process_args(args: argparse.Namespace):
	if args.debug:
		print(args)

	# Tree Level
	if args.max_main_group:
		args.max_hirarchy = 0
	if args.max_sub_group is not None:
		args.max_hirarchy = args.max_sub_group
	if args.max_description:
		args.max_hirarchy = "description"
	if args.max_extra_details_keys:
		args.max_hirarchy = "extra_details_keys"
	if args.max_extra_details_values:
		args.max_hirarchy = "extra_details_values"

	# Sorting
	if args.alphabetical:
		args.sort_method = SortingMethods.alphabetical
	if args.total_time:
		args.sort_method = SortingMethods.total_time

	return args
