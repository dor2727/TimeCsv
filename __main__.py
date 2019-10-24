#!/usr/bin/rlwrap python3

import Time.statistics
import sys
import os

def newest(path):
	files = os.listdir(path)
	paths = [os.path.join(path, basename) for basename in files]
	return max(paths, key=os.path.getctime)

def main():
	a = Time.statistics.TimeParser(path=newest("/home/me/Dropbox/Projects/Time/data"))

	arg = 1 # default value
	if len(sys.argv) > 1:
		if sys.argv[1].isdigit():
			arg = int(sys.argv[1])

	if type(arg) is int:
		a.basic_stats(arg)
	else:
		a.basic_stats_by_description(sys.argv[1])


if __name__ == '__main__':
	main()
	