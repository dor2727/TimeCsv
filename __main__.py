#!/usr/bin/rlwrap python3

import Time.statistics
import sys
import os
import argparse
import datetime

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

def newest(path):
	files = os.listdir(path)
	paths = [os.path.join(path, basename) for basename in files]
	return max(paths, key=os.path.getctime)

def main():
	a = Time.statistics.TimeParser(path=newest("/home/me/Dropbox/Projects/Time/data"))

	args = parse_args()
	if args.months_back is None:
		search_string = ' '.join(args.search_string)

		end_date = datetime.datetime.now()
		start_date = Time.statistics.get_midnight(end_date - datetime.timedelta(days=args.days_back))

		if args.debug:
			print(( start_date, end_date ))
		
		a.basic_stats_by_description(search_string, date_range=( start_date, end_date ))
	else:
		a.basic_stats(args.months_back)



if __name__ == '__main__':
	main()
	