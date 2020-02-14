#!/usr/bin/rlwrap python3

import os
import sys
import argparse
import datetime

import TimeNew.statistics
from TimeNew.time_utils import newest

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--days-back", "-d", type=int , default=7   , dest='days_back'  , help="how many days back to query")
	parser.add_argument("--month",     "-m", type=int , default=None, dest='months_back', help='how many month summaries to show')
	parser.add_argument("--debug"          , action="store_true")
	parser.add_argument("search_string"    , type=str , default=''  , nargs=argparse.REMAINDER)

	args = parser.parse_args()

	if args.debug:
		print(args)

	return args

def main():
	filename = newest("/home/me/Dropbox/Projects/Time/data")
	print(filename)
	a = TimeNew.statistics.DataFile(path=filename)
	print(a._validate_data())

	b = TimeNew.statistics.DataFolder("/home/me/Dropbox/Projects/Time/data")
	print(b)
	import pdb; pdb.set_trace()


if __name__ == '__main__':
	print(1)
	main()
	