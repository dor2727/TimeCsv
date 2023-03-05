import json
import functools
import numpy as np
import matplotlib.pyplot as plt

from TimeCsv.consts import	DEFAULT_PIE_PATH
from TimeCsv.utils import 	shorten_selected_time, \
							format_dates         , \
							seconds_to_str       , \
							seconds_to_hours_str


class Stats(object):
	def __init__(self, data, time_filter=None):
		self.data = data
		self._time_filter = time_filter


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

	@property
	def time_between_events_on_average(self):
		# return in seconds
		if self.amount_of_items == 0:
			return 0
		if self.amount_of_items == 1:
			return 0

		return (self.amount_of_days * 24 * 60 * 60) / self.amount_of_items


	#
	# Exposing different ways of printing the data
	#
	def __repr__(self):
		return self.__class__.__name__

	@property
	def selected_time(self):
		if self._time_filter is None:
			return "All time"

		return self._time_filter.selected_time

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
		raise NotImplemented

	def to_telegram(self):
		return self.to_text()

	def to_dict(self):
		raise NotImplemented

	def to_csv(self):
		items = self.to_dict().items()
		# sort by keys
		items = sorted(items, key=lambda x: x[0])

		headers = [i[0] for i in items]
		values = [i[1] for i in items]
		return ','.join(headers) + '\n' + ','.join(values)

	def to_json(self):
		return json.dumps(self.to_dict(), sort_keys=True)

	def to_pie(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the pie chard
		if save is str: save the image to that path
		if save is True: save to the default location
		"""
		raise NotImplemented

	def to_bar(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the bar graph
		if save is str: save the image to that path
		if save is True: save to the default location
		"""
		raise NotImplemented


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
		s += "    (%3d) : %s (%5.2f%%) │ item average %s │ distance average %s" % (
			self.amount_of_items,
			seconds_to_str(self.amount_of_time),
			self.time_percentage,
			seconds_to_str(self.amount_of_time_on_average),
			seconds_to_str(self.time_between_events_on_average),
		)

		return s


def require_processed_data(func):
	@functools.wraps(func)
	def inner(self, *args, **kwargs):
		if not (hasattr(self, "titles_sorted") and hasattr(self, "values_sorted")):
			self.process_data()
		return func(self, *args, **kwargs)
	return inner

class DetailedStats(Stats):
	_allowed_grouping_methods = ("time", "time_average", "amount")
	_allowed_sorting_methods  = ("alphabetically", "by_value")

	def __init__(self, data, time_filter=None, grouping_method="time", sorting_method="by_value"):
		super().__init__(data, time_filter)

		self._grouping_method = grouping_method.lower()
		if self._grouping_method not in self._allowed_grouping_methods:
			raise ValueError(f"invalid grouping_method: {grouping_method}")

		self._sorting_method = sorting_method.lower()
		if self._sorting_method not in self._allowed_sorting_methods:
			raise ValueError(f"invalid sorting_method: {sorting_method}")


	#
	# Required functions
	#
	def _get_titles(self):
		raise NotImplemented

	def _get_items_of_title(self, title):
		if hasattr(self, "_get_filter_of_title") and callable(self._get_filter_of_title):
			return self._get_filter_of_title(title).get_filtered_data(self.data)

		raise NotImplementedError


	#
	# Process & sort titles & values
	#
	def process_data(self):
		"""
		processes self.data
		return 2 lists
			1) titles: each item is the name of the group
			2) values: each item is a list with the items
		"""
		titles = self._titles = self._get_titles()

		values = self._values = list(map(
			self._get_data_of_title,
			titles
		))

		self.titles_sorted, self.values_sorted = self._sort(titles, values)
		return self.titles_sorted, self.values_sorted

	def _sort(self, titles, values):
		# if either headers or values are empty
		if not titles or not values:
			return titles, values

		z = zip(titles, values)

		# sort by title (str), alphabetically
		if self._sorting_method == "alphabetically":
			sorted_z = sorted(z, key=lambda i: i[0])
		# sort by value, highest first
		elif self._sorting_method == "by_value":
			sorted_z = sorted(z, key=lambda i: i[1], reverse=True)
		else:
			raise ValueError("invalid sorting_method")

		# unpack the zip into titles and values
		t, v = tuple(zip(*sorted_z))
		return t, v

	def _get_all_data_of_title(self, title):
		items = self._get_items_of_title(title)

		amount_of_items = len(items)
		amount_of_time = sum(items)

		if amount_of_items:
			amount_of_time_on_average = amount_of_time / amount_of_items
			if amount_of_items == 1:
				time_between_events_on_average = 0
			else:
				time_between_events_on_average = (self.amount_of_days * 24 * 60 * 60) / amount_of_items
		else:
			amount_of_time_on_average = 0
			time_between_events_on_average = 0

		return amount_of_items, amount_of_time, amount_of_time_on_average, time_between_events_on_average

	def _get_data_of_title(self, title):
		amount_of_items, amount_of_time, amount_of_time_on_average, time_between_events_on_average = self._get_all_data_of_title(title)

		if self._grouping_method == "time":
			return amount_of_time
		elif self._grouping_method == "amount":
			return amount_of_items
		elif self._grouping_method == "time_average":
			return amount_of_time_on_average
		else:
			raise ValueError(f"invalid grouping_method: {self._grouping_method}")

	#
	# Plot utils
	#
	@property
	def title(self):
		return getattr(
			self,
			"_title",
			(
				f"{getattr(self, '_title_prefix', '')}"
				f"{self.__class__.__name__}"
				f"({self._grouping_method})"
				 " - "
				f"{self.selected_time}"
			)
		)

	@title.setter
	def title(self, value):
		self._title = value

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

	def _plot_set_title(self, fig, ax):
		ax.set_title(self.title)
		fig.canvas.manager.set_window_title(self.title)
		# fig.canvas.set_window_title(self.title)

	def _plot_make_pie(self, ax, values, titles):
		def pct(value):
			# value is given as a percentage - a float between 0 to 100
			hours_str = seconds_to_hours_str(value * self.amount_of_time / 100)
			return f"{value:.1f}%\n{hours_str}h"

		# making the pie chart
		patches, _, _ = ax.pie(values, labels=titles, autopct=pct)
		ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

		return patches

	def _plot_make_bar(self, ax, values, titles):
		# making the bar graph
		x = np.arange(len(titles))  # the label locations
		width = 0.35  # the width of the bars
		rects = ax.bar(x, values, width)

		# titles & labels
		ax.set_ylabel(self._grouping_method)
		ax.set_xticks(x)
		ax.set_xticklabels(titles)

		return rects

	#
	# Plotting
	#
	@require_processed_data
	def to_pie(self, save=True):
		"""
		if save:
			return open handle to the file with the image

			if save is str:
				save the image to that path
			if save is True:
				save to the default location

		if bool(save) is False:
			interactively show the pie chard
		"""
		# plotting initialization
		fig, ax = plt.subplots()

		patches = self._plot_make_pie(ax, self.values_sorted, self.titles_sorted)

		if hasattr(self, "_plot_make_pie_clickable"):
			self._plot_make_pie_clickable(fig, patches)

		self._plot_set_title(fig, ax)

		return self._plot_save(fig, save)

	@require_processed_data
	def to_bar(self, save=True):
		"""
		if save:
			return open handle to the file with the image

			if save is str:
				save the image to that path
			if save is True:
				save to the default location

		if bool(save) is False:
			interactively show the pie chard
		"""
		# plotting initialization
		fig, ax = plt.subplots()

		self._plot_make_bar(ax, self.values_sorted, self.titles_sorted)

		self._plot_set_title(fig, ax)

		return self._plot_save(fig, save)


	#
	# Text utils
	#
	def _generate_text(self, header, text_per_item, footer):
		s  = header()

		for t in self.titles_sorted:
			s += "\n"
			s += text_per_item(t)

		s += "\n"
		s += footer()

		return s

	@property
	def _text_title_format(self):
		return "%%-%ds" % (max(map(len, self.titles_sorted), default=1) + 1)

	def _text_generate_header(self):
		s  = self.time_representation_str
		s += "\n"
		s += f"  events per day = {self.events_per_day:.2f}"
		return s

	def _text_generate_footer(self):
		if not self.titles_sorted:
			return "    No titles found :("
		if not self.amount_of_items:
			return "    No items found :("

		s  = "    " + '-'*50
		s += "\n"
		s += "    %s (%4d) : %s" % (
			(self._text_title_format % "Total"),
			self.amount_of_items,
			seconds_to_str(self.amount_of_time),
		)
		return s

	def _text_generate_item(self, title):
		amount_of_items, amount_of_time, amount_of_time_on_average, time_between_events_on_average = self._get_all_data_of_title(title)

		time_percentage = amount_of_time / self.amount_of_time * 100.0

		return "    %s (%4d) : %s (%5.2f%%) │ item average %s │ distance average %s" % (
			(self._text_title_format % title),
			amount_of_items,
			seconds_to_str(amount_of_time),
			time_percentage,
			seconds_to_str(amount_of_time_on_average),
			seconds_to_str(time_between_events_on_average),
		)

	def _telegram_generate_item(self, title):
		amount_of_items, amount_of_time, amount_of_time_on_average, time_between_events_on_average = self._get_all_data_of_title(title)

		time_percentage = amount_of_time / self.amount_of_time * 100.0

		return "    %s\n        (%4d) : %s (%5.2f%%)" % (
			(self._text_title_format % title),
			amount_of_items,
			seconds_to_str(amount_of_time),
			time_percentage,
		)

	#
	# Printing
	#
	@require_processed_data
	def to_text(self):
		return self._generate_text(
			self._text_generate_header,
			self._text_generate_item,
			self._text_generate_footer
		)

	@require_processed_data
	def to_telegram(self):
		return self._generate_text(
			self._text_generate_header,
			self._telegram_generate_item,
			self._text_generate_footer
		)


class DetailedStatsFiltered(DetailedStats):
	def __init__(self, data, filter_obj, time_filter=None, grouping_method="time", sorting_method="by_value"):
		super().__init__(data, time_filter, grouping_method, sorting_method)

		self._filter_obj = filter_obj

		self._initialize_data()

	def _initialize_data(self):
		self._original_data = self.data
		self.data = self._filter_obj % self.data
