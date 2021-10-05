#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import math

from TimeCsv import DataFolder, \
					filter_sleep

BASE_HOUR = 18 # 6PM

#
# Utils
#
def shift(d):
	"""
		input: datetime.datetime
		convert hours & minutes to a single number, measured in hours
		which ranges from BASE_HOUR to BASE_HOUR in the next day
		so that the time in which we sleep will be in the middle
	"""
	hour = d.hour + d.minute/60

	hour -= BASE_HOUR

	if hour < 0:
		hour += 24

	return hour

def list_to_bins(l, bin_size=10):
	return np.array([
		np.mean(l[ i*bin_size:(i+1)*bin_size ])
		for i in range(math.ceil( len(l) / bin_size ))
	])

#
# Data processing
#
def get_sleep_data(data):
	sleep_start = np.array([
		shift(i.start_time)
		for i in data
	])
	sleep_stop  = np.array([
		shift(i.stop_time)
		for i in data
	])
	return sleep_start, sleep_stop

def get_midsleep(start, stop):
	diff = stop - start

	return start + (diff / 2)


def print_basic_sleep_statistics(sleep_start, sleep_stop):
	def pprint(name, l):
		print(f"sleep {name:6s} average: {l.mean() + BASE_HOUR}")

	pprint("start" , sleep_start)
	pprint("stop"  , sleep_stop)
	pprint("middle", get_midsleep(sleep_start, sleep_stop))
	pprint("length", sleep_stop - sleep_start)
	print(f"len items: {len(sleep_start)}")


#
# Plot utils
#
# The X axis represents the hours. Plot only several key hours (this won't clutter the X axis)
def set_x_ticks(ticks_locations=[0, 5, 10, 15, 20, 24]):
	x_ticks_locations = np.array(ticks_locations)

	# create text for the locations that will be marked
	format_hour = lambda h: f"{h if h<24 else h-24:02d}:00"
	x_ticks_lables = [
		format_hour(i + BASE_HOUR)
		for i in x_ticks_locations
	]

	# add silent ticks to all the other locations
	full_ticks_locations = list(range(
		min(x_ticks_locations),
		max(x_ticks_locations) + 1
	))
	full_ticks_labels = [
		(
			x_ticks_lables[ np.where(x_ticks_locations == i)[0][0] ]
			if i in x_ticks_locations
			else ''
		)
		for i in full_ticks_locations
	]

	plt.xticks(full_ticks_locations, full_ticks_labels)

def plot_sleep_times(sleep_start, sleep_stop, bin_size=None):
	if bin_size:
		avg = lambda l: list_to_bins(l, bin_size)
	else:
		avg = lambda l: l

	start  = avg(sleep_start)
	stop   = avg(sleep_stop)
	middle = avg(get_midsleep(sleep_start, sleep_stop))

	# the y axis goes up as time progresses. The more recent the event, the higher it will be
	index = range(len(start))
	plt.scatter(start , index, c="red"  , label="Start" )
	plt.scatter(stop  , index, c="green", label="Stop"  )
	plt.scatter(middle, index, c="blue" , label="Middle")

	set_x_ticks()

	plt.show()


def _remove_outliers(sleep_start, sleep_length):
	# manually remove a sleep length outlier (-21 hours. probably because I slept before 18:00?)
	index = np.where(sleep_length == min(sleep_length))
	sleep_start  = np.delete(sleep_start , index)
	sleep_length = np.delete(sleep_length, index)

	# manually remove sleep start outliers (sleeping after 5:00, which is 11 hours after 18:00)
	index = np.where(sleep_start > 11)
	sleep_start  = np.delete(sleep_start , index)
	sleep_length = np.delete(sleep_length, index)

	return sleep_start, sleep_length

def plot_sleep_length_as_a_function_of_sleep_start(sleep_start, sleep_stop):
	sleep_length = sleep_stop - sleep_start

	# clean data
	sleep_start, sleep_length = _remove_outliers(sleep_start, sleep_length)

	# fit
	fit = np.polyfit(sleep_start, sleep_length, 1) # linear fit

	# plot data
	plt.scatter(sleep_start, sleep_length, c="red")

	# plot fit
	x = np.linspace(min(sleep_start), max(sleep_start), len(sleep_start)*2)
	p = np.poly1d(fit)
	plt.plot(x, p(x), c="green", label=f"{fit[1]:.2f} {fit[0]:.2f} h")

	# prettify graph
	set_x_ticks(ticks_locations=[2, 5, 8, 11])

	plt.xlabel("sleep start time")
	plt.ylabel("sleep duration [hours]")
	plt.legend()
	plt.show()


def get_sleep_statistics(datafolder=None, time_filter=None):
	datafolder = datafolder or DataFolder()

	data = filter_sleep % datafolder.data

	if time_filter:
		data = time_filter % data

	sleep_start, sleep_stop = get_sleep_data(data)

	print_basic_sleep_statistics(sleep_start, sleep_stop)

	# plot_sleep_times(sleep_start, sleep_stop)
	# plot_sleep_times(sleep_start, sleep_stop, bin_size=10)

	plot_sleep_length_as_a_function_of_sleep_start(sleep_start, sleep_stop)


if __name__ == '__main__':
	get_sleep_statistics()
