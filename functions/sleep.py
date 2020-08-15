import numpy as np
import matplotlib.pyplot as plt
import math

from TimeCsv.parsing import DataFolder
from TimeCsv.filters import *
from TimeCsv.filters_special import filter_sleep

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

def print_sleep_start_end_middle(sleep_start, sleep_stop, sleep_middle, sleep_length):
	print(f"sleep start  average: {sleep_start.mean() + 18}")
	print(f"sleep stop   average: {sleep_stop.mean() + 18}")
	print(f"sleep middle average: {sleep_middle.mean() + 18}")
	print(f"sleep length average: {sleep_length.mean()}")
	print(f"len items: {len(sleep_start)}")

def plot_sleep_start_end_middle(sleep_start, sleep_stop, sleep_middle):
	# the y axis goes up as time progresses. The more recent the event, the higher it will be
	l = len(sleep_start)
	plt.scatter(sleep_start , range(l), c="red")
	plt.scatter(sleep_stop  , range(l), c="green")
	plt.scatter(sleep_middle, range(l), c="blue")
	set_x_ticks()
	plt.show()
	import pdb; pdb.set_trace()

def plot_sleep_start_end_middle_averaged(sleep_start_avg, sleep_stop_avg, sleep_middle_avg):
	# the y axis goes up as time progresses. The more recent the event, the higher it will be
	l = len(sleep_start_avg)
	plt.scatter(sleep_start_avg , range(l), c="red")
	plt.scatter(sleep_stop_avg  , range(l), c="green")
	plt.scatter(sleep_middle_avg, range(l), c="blue")
	set_x_ticks()
	plt.show()
	import pdb; pdb.set_trace()

def plot_sleep_length_as_a_function_of_sleep_start(sleep_start, sleep_length):
	# manually remove a sleep length outlier (-21 hours. probably because I slept before 18:00?)
	index = np.where(sleep_length == min(sleep_length))
	sleep_start  = np.delete(sleep_start , index)
	sleep_length = np.delete(sleep_length, index)

	# manually remove sleep start outliers (sleeping after 5:00, which is 11 hours after 18:00)
	index = np.where(sleep_start > 11)
	sleep_start  = np.delete(sleep_start , index)
	sleep_length = np.delete(sleep_length, index)

	fit = np.polyfit(sleep_start, sleep_length, 1) # linear fit

	plt.scatter(
		sleep_start,
		sleep_length,
		c="red"
	)

	x = np.linspace(min(sleep_start), max(sleep_start), len(sleep_start)*2)
	p = np.poly1d(fit)
	plt.plot(x, p(x), c="green", label=f"{fit[1]:.2f} {fit[0]:.2f} h")

	set_x_ticks(l=[2, 5, 8, 11])

	plt.xlabel("sleep start time")
	plt.ylabel("sleep duration [hours]")
	plt.legend()
	plt.show()
	import pdb; pdb.set_trace()

# this is sleep_main
def get_sleep_statistics(datafolder=None):
	datafolder = datafolder or DataFolder()
	# using --all-time, so no time filter is needed

	data = filter_sleep % datafolder.data
	# data = ((TimeFilter_Month(3) | TimeFilter_Month(4) | TimeFilter_Month(5)) & filter_sleep) % datafolder.data

	sleep_start, sleep_stop, sleep_middle, sleep_start_avg, sleep_stop_avg, sleep_middle_avg = group_sleep_data(data)

	sleep_length = sleep_stop - sleep_start

	print_sleep_start_end_middle(sleep_start, sleep_stop, sleep_middle, sleep_length)

	return
	# plot_sleep_start_end_middle(sleep_start, sleep_stop, sleep_middle, sleep_length)

	plot_sleep_length_as_a_function_of_sleep_start(sleep_start, sleep_length)

	# plot_sleep_start_end_middle_averaged(sleep_start_avg, sleep_stop_avg, sleep_middle_avg)

