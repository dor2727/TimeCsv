#!/usr/bin/env python3
import os
import re
import csv
import sys
import utils
import calendar
import datetime

import Time.plotters as plotters
from Time.consts import *
from Time.time_utils import *


class Data(object):
	def __init__(self, items):
		if self._check_if_comment(items):
			return

		self._items = []
		for i in range(len(self.PARSERS)):
			self._items.append(
				self.PARSERS[i](items[i])
			)

	def __getitem__(self, n):
		return self._items[n]

	def __repr__(self):
		return "%s : %s : %s : %-14s : %s" % (
			self._str_date(),
			self._str_start_time(),
			self._str_stop_time(),
			self._str_group(),
			self._str_description(),
		)

	def __int__(self):
		return (self.stop_time - self.start_time).seconds

	def _check_if_comment(self, items):
		if not items:
			# if items is an empty list - [] - then the line is empty
			self.is_comment = True
			return True
		if items[0][0] == '#':
			self.is_comment = True
			return True
		else:
			self.is_comment = False
			return False

	@property
	def friends(self, raw=False):
		# get all from the patterns
		found = (
			PATTERN_WITH.findall(self.description)
			 +
			PATTERN_FOR .findall(self.description)
			 +
			PATTERN_TO  .findall(self.description)
		)

		if raw:
			return found
		else:
			# join all results into one string
			found = ' '.join(i[0] for i in found)
		
			return found.replace("and", "").split()

	def _parser_date(self, s):
		if s == COPY_LAST_DATE:
			self.date = COPY_LAST_DATE
		elif s == ADD_LAST_DATE:
			self.date = ADD_LAST_DATE
		else:
			self.date = datetime.datetime.strptime(s, "%Y/%m/%d")
		return self.date
	def _parser_start_time(self, s):
		if s == COPY_LAST_START_TIME:
			self.start_time = COPY_LAST_START_TIME
		else:
			start_time = datetime.datetime.strptime(s, "%H:%M")
			if type(self.date) is str:
				self.start_time = datetime.timedelta(
					hours=start_time.hour,
					minutes=start_time.minute,
				)
			else:
				self.start_time = datetime.datetime(
					year  =self.date.year,
					month =self.date.month,
					day   =self.date.day,
					hour  =start_time.hour,
					minute=start_time.minute,
				)
		return self.start_time
	_STOP_INITIALS     = ('s', 'e')
	_DURATION_INITIALS = ('d')
	def _parser_stop_time(self, s):
		if s == COPY_LAST_STOP_TIME:
			self.stop_time_type = "copy"
			self.stop_time = COPY_LAST_STOP_TIME
		else:
			if s[0] in self._STOP_INITIALS:
				self.stop_time_type = "stop"
				stop_time = datetime.datetime.strptime(s[1:], "%H:%M")
				if type(self.date) is str:
					self.stop_time = datetime.timedelta(
						hours=stop_time.hour,
						minutes=stop_time.minute,
					)
				else:
					self.stop_time = datetime.datetime(
						year  =self.date.year,
						month =self.date.month,
						day   =self.date.day,
						hour  =stop_time.hour,
						minute=stop_time.minute,
					)
			elif s[0] in self._DURATION_INITIALS:
				self.stop_time_type = "duration"
				duration = datetime.datetime.strptime(s[1:], "%H:%M")
				# it will be added to self.start_time at self._reevaluate_start_time
				self.stop_time = datetime.timedelta(
					hours=duration.hour,
					minutes=duration.minute,
				)
		return self.stop_time
	def _parser_group(self, s):
		self.group = s
		return s
	def _parser_description(self, s):
		self.description = s
		return s
	@property
	def PARSERS(self):
		return [
			self._parser_date,
			self._parser_start_time,
			self._parser_stop_time,
			self._parser_group,
			self._parser_description,
		]
	def _str_date(self):
		if type(self.date) is str:
			return self.date
		else:
			return self.date.strftime("%Y/%m/%d")
	def _str_start_time(self):
		if type(self.start_time) is str:
			return self.start_time
		elif type(self.start_time) is datetime.timedelta:
			return int(self.start_time.total_seconds())
		else:
			return self.start_time.strftime("%H:%M")
	def _str_stop_time(self):
		days = "    "

		if type(self.stop_time) is str:
			hour = self.stop_time
		elif type(self.stop_time) is datetime.timedelta:
			hour = int(self.stop_time.total_seconds())
		else:
			hour = self.stop_time.strftime("%H:%M")
			if get_ymd_tuple(self.start_time) != get_ymd_tuple(self.stop_time):
				days = "(+%d)" % ((self.stop_time - self.start_time).days + 1)
		return hour + ' ' + days

	def _str_group(self):
		return self.group
	def _str_description(self):
		return self.description

	def _reevaluate_date(self, prev, next=None):
		if type(self.date) is str:
			if self.date == COPY_LAST_DATE:
				self.date = prev.date
			elif self.date == ADD_LAST_DATE:
				self.date = prev.date + datetime.timedelta(days=365)

		if type(self.start_time) is datetime.timedelta:
			try:
				self.start_time = self.date + self.start_time
			except:
				import pdb; pdb.set_trace()
		if type(self.stop_time) is datetime.timedelta and self.stop_time_type == "stop":
			try:
				self.stop_time = self.date + self.stop_time
			except:
				import pdb; pdb.set_trace()
	def _reevaluate_start_time(self, prev, next=None):
		if type(self.start_time) is str:
			if self.start_time == COPY_LAST_START_TIME:
				self.start_time = prev.stop_time
		elif type(self.start_time) is datetime.timedelta:
			self.start_time = self.date + self.start_time

		if type(self.stop_time) is datetime.timedelta and self.stop_time_type == "duration":
			self.stop_time = self.start_time + self.stop_time
	def _reevaluate_stop_time(self, prev, next):
		if type(self.stop_time) is str:
			if self.stop_time == COPY_LAST_STOP_TIME:
				self.stop_time = next.start_time
				# if next.start_time is not set (for example, if next.date is "----/--/--"), then we treat it as if
				# self.stop_time_type is 'stop', since next.start_time should be set fixed
				if type(self.stop_time) is datetime.timedelta:
					self.stop_time = self.date + self.stop_time

		if self.stop_time < self.start_time:
			self.stop_time += datetime.timedelta(days=1)
	def reevaluate(self, prev, next):
		self._reevaluate_date(prev, next)
		self._reevaluate_start_time(prev, next)
		self._reevaluate_stop_time(prev, next)

	def is_in_date_range(self, start_date, end_date, inclusive=True):
		"""
		returns True if:
			The whole Data object        is contained within the date_range
			inclusive && Data.start_time is contained within the date_range
		"""
		if (start_date <= self.start_time) and (self.stop_time <= end_date):
			return True
		if inclusive and (start_date <= self.start_time <= end_date):
			return True
		return False

class TimeParser(object):
	def __init__(self, path=None):
		self._path = path or self.file_path
		self._load_data(self._path)
		self._reevaluate_data()
		self._create_titles()
		self._create_friends_list()

		# self.plot = Plotter(self, "_plot")
		# self.plot = plotters.Plot(get_data=self.get_data)
	
	def reload(self):
		self._load_data(self._path)
		self._reevaluate_data()
		self._create_titles()
		self._create_friends_list()

	@property
	def file_path(self):
		path_without_extension = os.path.join(DEFAULT_DATA_DIRECTORY, self.__class__.__name__)
		for e in POSSIBLE_FILE_EXTENSIONS:
			if os.path.exists(path_without_extension + e):
				return path_without_extension + e
		else:
			raise OSError("file not found (%s)" % path_without_extension)

	def _load_data(self, path):
		r = csv.reader(
			open(
				os.path.expandvars(
					os.path.expanduser(
						path
					)
				)
			)
		)
		self.headers = next(r)
		self.data = list(filter(
			# filter out comment lines
			lambda x: not x.is_comment,
			map(
				# parse each line
				lambda x: Data(x),
				r
			)
		))

	def _reevaluate_data(self):
		# ignoring first and last, which doesnt have 'prev' and 'next' respectivly
		for i in range(len(self.data[1:-1])):
			self.data[i+1].reevaluate(self.data[i], self.data[i+2])
		self.data[-1].reevaluate(self.data[-2], None)

	def _create_titles(self):
		# iterate every item in the data, collect its group into a unique list
		self.titles = list(set(i.group for i in self.data))
		self.titles.sort()

	def _create_friends_list(self):
		all_friends = sum((i.friends for i in self.data), [])

		self.friends_histogram = utils.counter(all_friends)
		# counter object is a list of tuples (name, amount)
		self.friends_histogram.sort(key=lambda x:x[1], reverse=True)

		self.friends = [i[0] for i in self.friends_histogram]

	def get_data(self, year=None, month=None, date_range=None):
		"""
		there are several options to call this method
		1) date_range as a tuple of 2 datetime objects - start end and, both are inclusive
		2) get_data() - all parameters will be None. all the items will be given
		3) only set year - the whole year will be given
		4) both year and month - the whole month will be given
		"""
		if date_range is not None:
			selected_time = "date range"
			days_representation = DATE_REPRESENTATION_PATTERN % (
				date_range[0].year,
				date_range[0].month,
				date_range[0].day,
				date_range[1].year,
				date_range[1].month,
				date_range[1].day,
			)
			filter_func = lambda i: i.is_in_date_range(*date_range)
			# filter_func = lambda i: date_range[0] <= i.date <= date_range[1]
		else:
			if month is None:
				if year is None:
					selected_time = "All times"
					# this is copied to another list, so self.data will not be changed
					filter_func = lambda i: True

					days_representation = DATE_REPRESENTATION_PATTERN % (
						self.data[ 0].date.year,
						self.data[ 0].date.month,
						self.data[ 0].date.day,
						self.data[-1].date.year,
						self.data[-1].date.month,
						self.data[-1].date.day,
					)
				else:
					selected_time = str(year)
					filter_func = lambda i: i.date.year == year
					days_representation = DATE_REPRESENTATION_PATTERN % (year, 1, 1, year, 12, 31)
			else:
				filter_func = lambda i: i.date.year == year and i.date.month == month
				days_representation = DATE_REPRESENTATION_PATTERN % (year, month, 1, year, month, calendar.monthrange(year, month)[1])
				selected_time = datetime.datetime(year=year, month=month, day=1).strftime("%Y - %m (%B)")

		items = list(filter( filter_func, self.data ))
		try:
			amount_of_days = (items[-1].date - items[0].date).days
		except:
			amount_of_days = 0
		time_representation = "%s (%s) (found %d days)" % (
			selected_time,
			days_representation,
			amount_of_days
		)
		return items, time_representation, amount_of_days

	def basic_stats(self, amount=None):
		# get month list
		months = list(set((i.date.year, i.date.month) for i in self.data))
		months.sort(key=lambda x: x[0]*12 + x[1])
		if amount:
			months = months[:amount]

		for m in months:
			items, time_representation, amount_of_days = self.get_data(*m)
			print(time_representation)

			# print basic statistics
			print("  events per day = %.2f" % (len(items) / amount_of_days))
			# print("  days per item = %.2f" % (amount_of_days / len(items)))
			# print("  avg per day   = %.2f" % (month_total / amount_of_days))
			# print("  avg per item  = %.2f" % (month_total / len(items)))

			month_total = sum(int(i) for i in items)
			for t in self.titles:
				title_items = list(filter(
					lambda x: x.group == t,
					items
				))
				total_seconds = sum(int(i) for i in title_items)
				print("    %-14s (%3d) : %s (%5.2f%%) ; item average %s" % (
					t,
					len(title_items),
					seconds_to_str(total_seconds),
					total_seconds / month_total * 100,
					seconds_to_str(total_seconds / len(title_items) if title_items else 0),
				))

			print("    " + '-'*57)
			print("    %-14s (%3d) : %2d days %2d hours %2d minutes" % (
				"Total",
				len(items),
				month_total // (60*60*24),
				month_total // (60*60) % (24),
				month_total // (60) % (60*24) % 60,
			))
			print()

	def basic_stats_by_description(self, s, year=None, month=None, date_range=None, case_sensitive=True):
		items, time_representation, amount_of_days = self.get_data(year, month, date_range)
		all_time_total = sum(int(i) for i in items)

		if case_sensitive:
			filter_func = lambda x: s in x.description
		else:
			filter_func = lambda x: s.lower() in x.description.lower()
		items = list(filter(filter_func, items))

		print(time_representation)
		print("  events per day = %.2f" % (len(items) / amount_of_days))
		total_seconds = sum(int(i) for i in items)

		print("(%3d) : %s (%5.2f%%) ; item average %s" % (
			len(items),
			seconds_to_str(total_seconds),
			total_seconds / all_time_total * 100,
			seconds_to_str(total_seconds / len(items) if items else 0),
		))


if __name__ == '__main__':
	import main
	main.main()
else:
	a = TimeParser(path="/home/me/Dropbox/Projects/Time/data/big_holiday_2019.tcsv")
	b = TelegramBotAPI(a.get_data)
	pass

