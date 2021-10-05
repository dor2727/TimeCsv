import os
import sys
import time
import traceback

from collections import OrderedDict, Counter

from TimeCsv.consts import *


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

def find_vehicle_in_str(s):
	for vehicle in VEHICLES:
		if f"by {vehicle}" in s:
			return vehicle
	return None


def counter(data):
    return list(Counter(data).items())
#
# regex utils
#
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

def re_exact(x):
	return f"\\b{x}\\b"

#
# datetime utils
#
def get_ymd_tuple(d):
	"ymd stands for Year, Month, Day"
	return (d.year, d.month, d.day)

def get_midnight(d):
	return datetime.datetime(*get_ymd_tuple(d))

def seconds_to_str(n):
	n = int(n)

	s = ''

	if days := (n // (60*60*24)):
		s += f"{days:3d} days"
	else:
		s += " " * (3+1+4)

	s += ' '

	if hours := (n // (60*60) % (24)):
		s += f"{hours:2d} hours"
	else:
		s += " " * (2+1+5)

	s += ' '

	if minutes := (n // (60) % (60*24) % 60):
		s += f"{minutes:2d} minutes"
	else:
		s += " " * (2+1+7)

	return s

def seconds_to_hours_str(n):
	h = n / (3600)
	return f"{h:.2f}"

def shorten_selected_time(selected_time):
	if len(selected_time) > 33:
		return "Multiple Time Filters"
	else:
		return selected_time

def format_dates(date1, date2):
	return DATE_REPRESENTATION_PATTERN % (
		*get_ymd_tuple(date1),
		*get_ymd_tuple(date2),
	)


#
# debug utils
#
def print_items(l, ret=False):
	if ret:
		return '\n'.join(i.__repr__() for i in l)
	else:
		print('\n'.join(i.__repr__() for i in l))
