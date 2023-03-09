import json
import math

from TimeCsv.utils.consts import DEFAULT_SELECTED_TIME
from TimeCsv.utils.types import Days, Seconds
from TimeCsv.utils.date_time import shorten_selected_time

# import functools
# import numpy as np
# import matplotlib.pyplot as plt

# from TimeCsv.consts import	DEFAULT_PIE_PATH
# from TimeCsv.utils import 	shorten_selected_time, \
# 							format_dates         , \
# 							seconds_to_str       , \
# 							seconds_to_hours_str

class DataHolder:
	def __init__(self, data, **kwargs):
		self.data = data

		self._set_selected_time(kwargs)

	def _set_selected_time(self, kwargs):
		if "time_filter" in kwargs:
			self._time_filter = kwargs["time_filter"]
			self.selected_time = self._time_filter.selected_time
		elif "selected_time" in kwargs:
			self.selected_time = kwargs["selected_time"]
		else:
			self.selected_time = DEFAULT_SELECTED_TIME


	#
	# Exposing different ways of printing the data
	#
	def __repr__(self):
		return self.__class__.__name__

class DataBasicStatistics(DataHolder):
	#
	# Exposing different properties of the data
	#
	@property
	def amount_of_items(self):
		return len(self.data)

	@property
	def amount_of_time(self) -> Seconds:
		return sum(map(int, self.data))

	@property
	def amount_of_days(self) -> Days:
		if self.data:
			return (self.data[-1].date - self.data[0].date).days + 1
		else:
			return 0
	@property
	def _amount_of_days_in_seconds(self) -> Seconds:
		return self.amount_of_days * 24 * 60 * 60

	@property
	def time_percentage(self):
		"""
			The percentage of time taken by self.data out of the total days in which self.data take place
		"""
		if self.amount_of_time == 0:
			return 0
		if not hasattr(self, "_time_filter"):
			return math.nan

		return self.amount_of_time / self._time_filter.total_time * 100


	@property
	def average_events_per_day(self):
		if self.amount_of_days == 0:
			return 0

		return self.amount_of_items / self.amount_of_days

	@property
	def average_event_time(self) -> Seconds:
		if self.amount_of_items == 0:
			return 0

		return self.amount_of_time / self.amount_of_items

	@property
	def average_time_between_events(self) -> Seconds:
		# return in seconds
		if self.amount_of_items == 0:
			return 0
		if self.amount_of_items == 1:
			return 0

		return _amount_of_days_in_seconds / self.amount_of_items

class DataPlotter(DataBasicStatistics):
	@property
	def date_representation(self) -> str:
		if self.data:
			return format_dates(self.data[0].date, self.data[-1].date)
		else:
			return "no days found"

	@property
	def time_representation(self) -> str:
		if hasattr(self, amount_of_days):
			suffix = " (found %d days)" % self.amount_of_days
		else:
			suffix = ""

		return "%s [%s]%s" % (
			shorten_selected_time(self.selected_time),
			self.date_representation,
			suffix
		)

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

	def to_json(self, fp=None):
		if fp is None:
			return json.dumps(self.to_dict(), sort_keys=True)
		else:
			return json.dump(self.to_dict(), fp, sort_keys=True)

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

