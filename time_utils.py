import os
import sys
import time
import traceback

from collections import OrderedDict, Counter

from TimeCsv.consts import *


LOG_FILE = open(os.path.join(TELEGRAM_DATA_DIRECTORY, "log.log"), "a")

# utils
def log(s):
	print(s)
	LOG_FILE.write(s)
	LOG_FILE.write('\n')
	LOG_FILE.flush()


#
# file utils
#

def read_telegram_file(filename):
	handle = open(os.path.join(
		TELEGRAM_DATA_DIRECTORY,
		filename
	))
	data = handle.read().strip()
	handle.close()
	return data

# get the newsest file
def newest(path=DEFAULT_DATA_DIRECTORY):
	files = os.listdir(path)
	paths = [os.path.join(path, basename) for basename in files]
	return max(paths, key=os.path.getctime)


#
# parsing utils
#
def find_friends_in_str(s, search_at_beginning=False):
	# get all from the patterns
	found = sum(
		(pattern.findall(s) for pattern in FRIEND_PATTERN),
		[]
	)
	if search_at_beginning:
		found += re.findall('^' + PATTERN_NAMES_LIST, s)

	# join all results into a big string
	found = ' '.join(i[0] for i in found)
	# remove 'and', and convert back into a list
	found = re.sub("\\band\\b", '', found)
	found = found.split()
	# unique
	return list(OrderedDict.fromkeys(found))

def find_location_in_str(s):
	if PATTERN_LOCATION_THEIR_PLACE in s:
		return "Their place"

	l = re.findall(PATTERN_LOCATION, s)
	if len(l) == 0:
		return None
	elif len(l) == 1:
		return l[0]
	else:
		return l

def counter(data):
    return list(Counter(data).items())

def re_escape(x):
	return ''.join(
		(
			'\\'+i
			 if
			i in re.sre_parse.SPECIAL_CHARS
			 else
			i
		)
		for i in x
	)

#
# datetime utils
#
def get_ymd_tuple(d):
	"ymd stands for Year, Month, Day"
	return (d.year, d.month, d.day)

def get_midnight(d):
	return datetime.datetime(*get_ymd_tuple(d))

def seconds_to_str(n):
	return ("%3d days %2d hours %2d minutes" % (
		n // (60*60*24),
		n // (60*60) % (24),
		n // (60) % (60*24) % 60,
	)).replace(" 0 days", "       ").replace(" 0 hours", "        ")

def seconds_to_hours_str(n):
	h = n / (3600)
	return f"{h:.2f}"
	
#
# debug utils
#
def print_items(l, ret=False):
	if ret:
		return '\n'.join(i.__repr__() for i in l)
	else:
		print('\n'.join(i.__repr__() for i in l))

def exception_message():
	exc_type, exc_value, exc_traceback = sys.exc_info()
	lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
	return ''.join('!! ' + line for line in lines)
