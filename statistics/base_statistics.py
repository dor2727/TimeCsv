import re
import json
import numpy as np
import matplotlib.pyplot as plt

# from TimeCsv.consts import *
# from TimeCsv.utils import *
# from TimeCsv.filters import *
from TimeCsv.utils import shorten_selected_time, format_dates, seconds_to_str

class Stats(object):
	def __init__(self, data, time_filter=None):
		self.data = data
		self._time_filter = time_filter


	#
	# Getting the data
	#
	def get_stats_dict(self):
		raise NotImplemented()

	def get_stats_list(self):
		"""
		return 2 lists - headers & values
		return them sorted
		"""
		raise NotImplemented()


	#
	# Exposing different properties of the data
	#
	@property
	def amount_of_items(self):
		return len(self.data)

	@property
	def amount_of_time(self):
		return sum(map(int, self.data))

	@property
	def amount_of_days(self):
		if self.data:
			return (self.data[-1].date - self.data[0].date).days + 1
		else:
			return 0

	@property
	def events_per_day(self):
		if self.amount_of_days == 0:
			return 0

		return self.amount_of_items / self.amount_of_days

	@property
	def amount_of_time_on_average(self):
		if self.amount_of_items == 0:
			return 0

		return self.amount_of_time / self.amount_of_items


	#
	# Exposing different ways of printing the data
	#
	def __repr__(self):
		return self.__class__.__name__

	@property
	def selected_time(self):
		if self._time_filter is None:
			return "All time"

		return self._time_filter.get_selected_time()

	@property
	def date_representation(self):
		if self.data:
			return format_dates(self.data[0].date, self.data[-1].date)
		else:
			return "no days found"

	@property
	def time_representation_str(self):
		return "%s [%s] (found %d days)" % (
			shorten_selected_time(self.selected_time),
			self.date_representation,
			self.amount_of_days
		)


	#
	# Exporing the data
	#
	def to_text(self):
		raise NotImplemented()

	def to_telegram(self):
		return self.to_text()

	def to_csv(self):
		items = self.get_stats_dict().items()
		# sort by keys
		items = sorted(items, key=lambda x: x[0])

		headers = [i[0] for i in items]
		values = [i[1] for i in items]
		headers, values = self.get_stats_list()
		return ','.join(headers) + '\n' + ','.join(values)

	def to_json(self):
		return json.dumps(self.get_stats_dict(), sort_keys=True)

	def to_pie(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the pie chard
		if save is str: save the image to that path
		if save is True: save to the default location
		"""
		raise NotImplemented()

	def to_bar(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the bar graph
		if save is str: save the image to that path
		if save is True: save to the default location
		"""
		raise NotImplemented()


class BasicStats(Stats):
	@property
	def time_percentage(self):
		"""
			The percentage of time taken by self.data out of the total days in which self.data take place
		"""
		if self.amount_of_time == 0:
			return 0

		return self.amount_of_time / self._time_filter.total_time * 100

	def to_text(self):
		s  = self.time_representation_str
		s += "\n"
		s += f"  events per day = {self.events_per_day:.2f}"
		s += "\n"
		s += "    (%3d) : %s (%5.2f%%) ; item average %s" % (
			self.amount_of_items,
			seconds_to_str(self.amount_of_time),
			self.time_percentage,
			seconds_to_str(self.amount_of_time_on_average),
		)

		return s


class AGenericStatsWithNoName(Stats):
	pass


"""
TODO
add a flag: "sort_by_value"
if true: sort the result of self.group by the values, and show the top values first
else: sort alphabetically or whatever
"""
class GroupedStats(Stats):
	_allowed_group_values = ("time", "time_average", "amount")
	_allowed_sorting_methods = ("alphabetically", "by_value")

	def __init__(self, data, selected_time="All times", group_value="time", sort="by_value"):
		self.data = data
		self.selected_time = selected_time

		self.group_value = group_value.lower()
		if self.group_value not in self._allowed_group_values:
			raise ValueError("invalid group_value: %s" % group_value)

		self._sorting_method = sort.lower()
		if self._sorting_method not in self._allowed_sorting_methods:
			raise ValueError("invalid sorting_method: %s" % sort)

		self.values_dict = {}

	#
	def _get_headers(self):
		"""
		return list
		and creates self._headers for caching
		"""
		raise NotImplemented()

	@property
	def headers(self):
		if hasattr(self, "headers_sorted"):
			return self.headers_sorted
		elif hasattr(self, "_headers"):
			return self._headers
		else:
			# create self._headers & sort them
			self.group()

			if hasattr(self, "headers_sorted"):
				return self.headers_sorted
			elif hasattr(self, "_headers"):
				return self._headers
			else:
				raise NameError("could not find headers")

	def _get_filtered_data_per_header(self, header):
		raise NotImplemented()

	def _set_value_of_header(self, header):
		items = self._get_filtered_data_per_header(header)

		self.values_dict[header] = {}
		self.values_dict[header]["amount_of_time"]  = amount_of_time  = sum(map(int, items))
		self.values_dict[header]["amount_of_items"] = amount_of_items = len(items)

		if items:
			self.values_dict[header]["item_average"] = amount_of_time / amount_of_items
		else:
			self.values_dict[header]["item_average"] = 0

	def _get_value_of_header(self, header):
		self._set_value_of_header(header)

		if self.group_value == "time":
			return self.values_dict[header]["amount_of_time"]
		elif self.group_value == "amount":
			return self.values_dict[header]["amount_of_items"]
		elif self.group_value == "time_average":
			return self.values_dict[header]["item_average"]
		else:
			raise ValueError

	def _sort(self, headers, values):
		# if either headers or values are empty
		if not headers or not values:
			return headers, values

		z = zip(headers, values)
		if self._sorting_method == "alphabetically":
			# sort by header (str), alphabetically
			sorted_z = sorted(z, key=lambda i: i[0])
		elif self._sorting_method == "by_value":
			# sort by value, highest first
			sorted_z = sorted(z, key=lambda i: i[1], reverse=True)
		else:
			raise ValueError("invalid sorting_method")
		# unpack the zip into headers and values
		h, v = list(zip(*sorted_z))
		return h, v

	def group(self):
		"""
		group self.data
		return 2 lists
		1) headers: each item is the name of the group
		2) values:  each item is a list with the items
		"""
		headers = self._get_headers()

		values = list(map(
			self._get_value_of_header,
			headers
		))

		self.headers_sorted, self.values_sorted = self._sort(headers, values)
		return self.headers_sorted, self.values_sorted

	#
	@property
	def title(self):
		return f"{self.__class__.__name__}({self.group_value}) - {self.selected_time}"

	def _plot_prepare_data(self, headers=None, values=None, title=None):
		# initializing values
		# todo: this can be written in a more compact way
		if headers is None:
			if not hasattr(self, "headers_sorted"):
				self.group()
			headers = self.headers_sorted
		if values is None:
			if not hasattr(self, "values_sorted"):
				self.group()
			values = self.values_sorted
		return headers, values

	def _plot_save(self, fig, save):
		if save:
			if save is True:
				path = DEFAULT_PIE_PATH
			else:
				path = save

			fig.savefig(path)
			plt.close(fig)

			return open(path, "rb")
		# plotting - interactive
		else:
			plt.show()
			return None

	def _plot_set_title(self, fig, ax, title=None):
		if title is None:
			title = self.title

		ax.set_title(title)
		fig.canvas.set_window_title(title)

	def _plot_make_pie(self, ax, values, headers):
		total_seconds = sum(values)
		def pct(value):
			# value is given as a percentage - a float between 0 to 100
			hours_str = seconds_to_hours_str(value * total_seconds / 100)
			return f"{value:.1f}%\n{hours_str}h"

		# making the pie chart
		patches, _, _ = ax.pie(values, labels=headers, autopct=pct)
		ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

		return patches

	def to_pie(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the pie chard
		if save is str: save the image to that path
		if save is True: save to the default location

		if save:
			return open handle to the file with the image
		"""
		headers, values = self._plot_prepare_data(headers, values)

		# plotting initialization
		fig, ax = plt.subplots()

		self._plot_make_pie(ax, values, headers)

		self._plot_set_title(fig, ax, title)

		return self._plot_save(fig, save)

	def _plot_make_bar(self, values, headers):
		# making the bar graph
		x = np.arange(len(headers))  # the label locations
		width = 0.35  # the width of the bars
		rects = ax.bar(x, values, width)

		# titles & labels
		ax.set_ylabel(self.group_value)
		ax.set_xticks(x)
		ax.set_xticklabels(headers)

	def to_bar(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the pie chard
		if save is str: save the image to that path
		if save is True: save to the default location

		if save:
			return open handle to the file with the image
		"""
		headers, values = self._plot_prepare_data(headers, values)

		# plotting initialization
		fig, ax = plt.subplots()

		self._plot_make_bar(values, headers)

		self._plot_set_title(fig, ax, title)

		return self._plot_save(fig, save)

	#
	def _generate_to_text_statistics_per_header(self, header, header_format, amount_of_time):
		self._get_value_of_header(header)
		stats = self.values_dict[header]

		stats["time_percentage"] = 100.0 * stats["amount_of_time"] / amount_of_time

		return "    %s (%4d) : %s (%5.2f%%) ; item average %s" % (
			(header_format % header),
			stats["amount_of_items"],
			seconds_to_str(stats["amount_of_time"]),
			stats["time_percentage"],
			seconds_to_str(stats["item_average"]),
		)
	def _generate_to_telegram_statistics_per_header(self, header, header_format, amount_of_time):
		self._get_value_of_header(header)
		stats = self.values_dict[header]

		stats["time_percentage"] = 100.0 * stats["amount_of_time"] / amount_of_time

		return "    %s\n        (%4d) : %s (%5.2f%%)\n          avg %s" % (
			(header_format % header),
			stats["amount_of_items"],
			seconds_to_str(stats["amount_of_time"]),
			stats["time_percentage"],
			seconds_to_str(stats["item_average"]),
		)

	def _generate_to_text_footer(self, header_format, amount_of_items, amount_of_time):
		s  = "    " + '-'*57
		s += "\n"
		s += "    %s (%4d) : %2d days %2d hours %2d minutes" % (
			(header_format % "Total"),
			amount_of_items,
			amount_of_time // (60*60*24),
			amount_of_time // (60*60) % (24),
			amount_of_time // (60) % (60*24) % 60,
		)
		return s

	def _generate_to_text_header(self, events_per_day):
		s  = self.time_representation_str
		s += "\n"
		s += f"  events per day = {events_per_day:.2f}"

		return s



	def _generate_text(self, header, statistics_per_header, footer):
		"""
		TODO
		and create a wrapper
			self._value
			that brings the relevant one based on self.group_value

		clean this function
		"""

		# calculate statistics for the whole time period
		amount_of_items = len(self.data)
		amount_of_time = sum(map(int, self.data))

		if amount_of_time == 0:
			events_per_day = 0
		else:
			amount_of_days = (self.data[-1].date - self.data[0].date).days + 1
			events_per_day = amount_of_items / amount_of_days

		s = header(events_per_day)

		if not amount_of_items:
			s += "\n    No items found :("
			return s

		# print per-header statistics
		header_format = "%%-%ds" % (max(map(len, self.headers), default=1) + 1)
		for h in self.headers:
			s += "\n"
			s += statistics_per_header(h, header_format, amount_of_time)

		s += "\n"
		s += footer(header_format, amount_of_items, amount_of_time)

		return s

	def to_text(self):
		return self._generate_text(
			self._generate_to_text_header,
			self._generate_to_text_statistics_per_header,
			self._generate_to_text_footer
		)

	def to_telegram(self):
		return self._generate_text(
			self._generate_to_text_header,
			self._generate_to_telegram_statistics_per_header,
			self._generate_to_text_footer
		)

