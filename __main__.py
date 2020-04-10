#!/usr/bin/rlwrap python3

import os
import sys
import argparse
import datetime

import TimeCsv.statistics
import TimeCsv.parsing
from TimeCsv.time_utils import newest
from TimeCsv.filters import *

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--days-back", "-d", type=int , default=7   , dest='days_back'  , help="how many days back to query")
	# parser.add_argument("--month",     "-m", type=int , default=None, dest='months_back', help='how many month summaries to show')
	parser.add_argument("--debug"          , action="store_true")
	parser.add_argument("--test"           , action="store_true")
	parser.add_argument("search_string"    , type=str , default=''  , nargs=argparse.REMAINDER)

	args = parser.parse_args()

	if args.debug:
		print(args)

	return args

def main():
	args = parse_args()

	if args.test:
		test(debug=args.debug)
		return

	b = TimeCsv.parsing.DataFolder()

	f = TimeFilter_Days(args.days_back)
	for s in args.search_string:
		f &= AutoFilter(s)

	if args.debug:
		print(f"filter: {f}")

	print(TimeCsv.statistics.FilteredStats(
		f % b.data,
		selected_time=f.selected_time
	).to_text())

def test(debug=False):
	# filename = newest()
	# if debug:
	# 	print(f"filename: {filename}")

	# a = TimeCsv.parsing.DataFile(path=filename)
	# if debug:
	# 	print(f"validating: {a._validate_data()}")

	b = TimeCsv.parsing.DataFolder("/home/me/Dropbox/Projects/Time/data")
	if debug:
		print(f"DataFolder: {b}")

	f = TimeFilter_Month(3) | TimeFilter_Month(4)
	f_data = f.get_filtered_data(b.data)
	print(len(f_data))

	# g = TimeCsv.statistics.GroupedStats_Games(f_data, group_value="amount")
	# g = TimeCsv.statistics.GroupedStats_Youtube(f_data, group_value="time")
	g = TimeCsv.statistics.GroupGroupedStats(f_data, group_value="time", category_name="Youtube")
	print(g.group())
	print(g.to_pie(save=False))

	import pdb; pdb.set_trace()


if __name__ == '__main__':
	print(1)
	main()
	