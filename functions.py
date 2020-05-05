import numpy as np
import matplotlib.pyplot as plt
import math

import TimeCsv.statistics
from TimeCsv.parsing import DataFolder
from TimeCsv.time_utils import newest
from TimeCsv.filters import *

def datetime_to_shifted_hour(d):
	# convert hours & minutes to a single number, measured in hours
	# which ranges from 6PM to 6PM in the next day
	# so that the time in which we sleep will be in the middle
	h = d.hour
	m = d.minute

	h -= 18
	if h < 0:
		h += 24
	h += m/60
	return h

def get_midsleep(start, stop):
	diff = stop - start

	return start + (diff / 2)

def group_sleep_data(data, group_size=10):
	sleep_start  = []
	sleep_stop   = []
	sleep_middle = []
	for i in data:
		sleep_start.append(datetime_to_shifted_hour(i.start_time))
		sleep_stop.append(datetime_to_shifted_hour(i.stop_time))
		sleep_middle.append(datetime_to_shifted_hour(get_midsleep(i.start_time, i.stop_time)))

	sleep_start  = np.array(sleep_start )
	sleep_stop   = np.array(sleep_stop  )
	sleep_middle = np.array(sleep_middle)

	sleep_start_avg  = np.array([
		np.mean(sleep_start[ i*group_size:(i+1)*group_size ])
		for i in range(math.ceil( len(sleep_start) / group_size ))
	])
	sleep_stop_avg  = np.array([
		np.mean(sleep_stop[ i*group_size:(i+1)*group_size ])
		for i in range(math.ceil( len(sleep_stop) / group_size ))
	])
	sleep_middle_avg  = np.array([
		np.mean(sleep_middle[ i*group_size:(i+1)*group_size ])
		for i in range(math.ceil( len(sleep_middle) / group_size ))
	])
	return sleep_start, sleep_stop, sleep_middle, sleep_start_avg, sleep_stop_avg, sleep_middle_avg

def get_sleep_statistics(datafolder=None):
	datafolder = datafolder or DataFolder()
	# using --all-time, so no time filter is needed

	# only "sleep" items, no "more sleep", and only items with more than 3 houts
	f = DescriptionFilter("sleep") & ~DescriptionFilter("more") & DurationFilter(f">{60*60*3}")
	data = f % datafolder.data

	sleep_start, sleep_stop, sleep_middle, sleep_start_avg, sleep_stop_avg, sleep_middle_avg = group_sleep_data(data)

	print(f"sleep start  average: {sleep_start.mean() + 18}")
	print(f"sleep stop   average: {sleep_stop.mean() + 18}")
	print(f"sleep middle average: {sleep_middle.mean() + 18}")
	print(f"len items: {len(data)}")

	# plot
	# the y axis goes up as time progresses. The more recent the event, the higher it will be
	l = len(data)
	plt.scatter(sleep_start , range(l), c="red")
	plt.scatter(sleep_stop  , range(l), c="green")
	plt.scatter(sleep_middle, range(l), c="blue")
	plt.show()
	
	l = len(sleep_start_avg)
	plt.scatter(sleep_start_avg , range(l), c="red")
	plt.scatter(sleep_stop_avg  , range(l), c="green")
	plt.scatter(sleep_middle_avg, range(l), c="blue")
	plt.show()
	import pdb; pdb.set_trace()

if __name__ == '__main__':
	get_sleep_statistics()
