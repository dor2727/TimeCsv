import os

from collections import OrderedDict

from TimeCsv.consts import *

#
# file utils
#

# get the newsest file
def newest(path=DEFAULT_DATA_DIRECTORY):
	files = os.listdir(path)
	paths = [os.path.join(path, basename) for basename in files]
	return max(paths, key=os.path.getctime)

#
# parsing utils
#
def find_friends_in_str(s):
	# get all from the patterns
	found = sum(
		(pattern.findall(s) for pattern in FRIEND_PATTERN),
		[]
	)

	# join all results into a big string
	found = ' '.join(i[0] for i in found)
	# remove 'and', and convert back into a list
	found = found.replace("and", "").split()
	# unique
	return list(OrderedDict.fromkeys(found))

#
# datetime utils
#
def get_ymd_tuple(d):
	"ymd stands for Year, Month, Day"
	return (d.year, d.month, d.day)

def get_midnight(d):
	return datetime.datetime(*get_ymd_tuple(d))

def seconds_to_str(n):
	return ("%2d days %2d hours %2d minutes" % (
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
