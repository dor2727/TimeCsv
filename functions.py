import numpy as np
import matplotlib.pyplot as plt
import math

import TimeCsv.statistics
from TimeCsv.parsing import DataFolder
from TimeCsv.time_utils import newest
from TimeCsv.filters import *
from TimeCsv.filters_special import filter_sleep


###############
###  SLEEP  ###
###############

def set_x_ticks(l=[0, 5, 10, 15, 20, 24]):
	# x_ticks_locs   = np.array([0, 5, 10, 15, 20, 24])
	x_ticks_locs   = np.array(l)
	x_ticks_lables = [
		f"{i if i<24 else i-24:02d}:00"
		for i in x_ticks_locs+18
	]
	plt.xticks(x_ticks_locs, x_ticks_lables)


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

# this is sleep_main
def get_sleep_statistics(datafolder=None):
	datafolder = datafolder or DataFolder()
	# using --all-time, so no time filter is needed

	data = filter_sleep % datafolder.data

	sleep_start, sleep_stop, sleep_middle, sleep_start_avg, sleep_stop_avg, sleep_middle_avg = group_sleep_data(data)

	sleep_length = sleep_stop - sleep_start

	print(f"sleep start  average: {sleep_start.mean() + 18}")
	print(f"sleep stop   average: {sleep_stop.mean() + 18}")
	print(f"sleep middle average: {sleep_middle.mean() + 18}")
	print(f"sleep length average: {sleep_length.mean()}")
	print(f"len items: {len(data)}")

	# plot
	# the y axis goes up as time progresses. The more recent the event, the higher it will be
	l = len(data)
	plt.scatter(sleep_start , range(l), c="red")
	plt.scatter(sleep_stop  , range(l), c="green")
	plt.scatter(sleep_middle, range(l), c="blue")
	set_x_ticks()
	plt.show()
	
	l = len(sleep_start_avg)
	plt.scatter(sleep_start_avg , range(l), c="red")
	plt.scatter(sleep_stop_avg  , range(l), c="green")
	plt.scatter(sleep_middle_avg, range(l), c="blue")
	set_x_ticks()
	plt.show()
	import pdb; pdb.set_trace()


##############
###  BLOG  ###
##############


class ExtraDetailsBlogStats(TimeCsv.statistics.GroupedStats):
	_extra_details_name = "sketch"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._filter_obj = (
			GroupFilter("Blog")
			 &
			DescriptionFilter(self._extra_details_name)
		)

		self._initialize_data()

	def _initialize_data(self):
		self._original_data = self.data
		self.data = self._filter_obj % self.data

	def _get_extra_details(self, obj):
		if not hasattr(obj, "extra_details"):
			return "<no extra details>"
		if not obj.extra_details:
			return "<no extra details>"
		e = obj.extra_details.get(self._extra_details_name, "<no extra details>")
		return e.split(EXTRA_DETAILS_SEPERATOR)[0]

	def _get_headers(self):
		# get all headers
		headers = set()

		for i in self.data:
			headers.add(self._get_extra_details(i))

		# return a list, sorted alphabetically
		self._headers = sorted(headers)
		return self._headers

	def _get_filtered_data_per_header(self, header):
		return list(filter(
			lambda i: self._get_extra_details(i) == header,
			self.data
		))

class ExtraDetailsBlogStats_sketch(ExtraDetailsBlogStats):
	_extra_details_name = "sketch"
class ExtraDetailsBlogStats_research(ExtraDetailsBlogStats):
	_extra_details_name = "research"
class ExtraDetailsBlogStats_manim(ExtraDetailsBlogStats):
	_extra_details_name = "manim"

def get_blog_statistics(datafolder=None):
	datafolder = datafolder or DataFolder()
	d = datafolder.data

	s = [
		ExtraDetailsBlogStats_sketch(d, group_value="time"),
		ExtraDetailsBlogStats_research(d, group_value="time"),
		ExtraDetailsBlogStats_manim(d, group_value="time"),
	]
	for g in s:
		print("==============")
		print("sketch")
		print("==============")
		print(g.group())
		print(g.to_pie(save=False))
		print("==============")
		# pdb to pause python and allow matplotlib to display the image
		import pdb; pdb.set_trace()

if __name__ == '__main__':
	# get_sleep_statistics()
	get_blog_statistics()
