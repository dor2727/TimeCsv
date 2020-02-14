import os

from collections import OrderedDict

from TimeNew.consts import *

#
# file utils
#

# get the newsest file
def newest(path):
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
