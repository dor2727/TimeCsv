import os
import re
import csv
import utils

from TimeCsv.consts import *
from TimeCsv.time_utils import *

class DataItem(object):
	"""
	comment lines are either empty lines or lines starting with '#'

	expected input for __init__ is a list of items in the following order:
		date        (str) (yyyy/mm/dd)
		start_time  (str) (hh:mm)
		end_time    (str) ('e'hh:mm) (e for End time, d for Duration)
		group       (str) (should start with a capital letter)
		description (str)

	the parsing should go as follows:
		first, this class should call each parser to store each value in its place
		then, the caller should iterate the 'reevaluate' method for each data object,
			with its 2 neighbors
		this way, place holders such as "My date is the same as the previous object date"
			(which is written as "----/--/--") will be evaluated

	exported functions:
		__int__:
			return the duration in seconds
		__getitem__:
			return the items in the csv order
		friends:
			return a list of friends which were in the activity
		reevaluate:
			used for calling 2nd parsing functions
		is_fully_parsed:
			checks whether this object has finished parsing, and is in a valid state
		is_in_date_range:
			checks whether this object is contained within a date range
	"""
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
			self._format_date(),
			self._format_start_time(),
			self._format_stop_time(),
			self._format_group(),
			self._format_description(),
		)

	# return total event time in seconds
	def __int__(self):
		return (self.stop_time - self.start_time).seconds

	def _check_if_comment(self, items):
		"""
		comment lines are either empty lines or lines starting with '#'
		"""
		if not items:
			# if items is an empty list - [] - then the line is empty
			self.is_comment = True
		elif items[0][0] == '#':
			self.is_comment = True
		else:
			self.is_comment = False

		return self.is_comment

	@property
	def friends(self):
		return find_friends_in_str(self.description)

	#
	# first parse iteration
	#
	def _parser_date(self, s):
		"""
		after this initial parsing, self.date will be:
			- str, if it was a special placeholder in the csv
			- datetime object, if it was a regular date value
		"""
		if s == COPY_LAST_DATE:
			self.date = COPY_LAST_DATE
		elif s == ADD_LAST_DATE:
			self.date = ADD_LAST_DATE
		else:
			self.date = datetime.datetime.strptime(s, "%Y/%m/%d")
		return self.date
	def _parser_start_time(self, s):
		"""
		after this initial parsing, self.start_time will be:
			- str, if it was a special placeholder in the csv
			- datetime object, if it was a regular start_time value
				and self.date is a datetime object
			- timedelta object, if it was a regular start_time value
				and self.date is str
		"""
		if s == COPY_LAST_START_TIME:
			self.start_time = COPY_LAST_START_TIME
		else:
			start_time = datetime.datetime.strptime(s, "%H:%M")
			if type(self.date) is str:
				self.start_time = datetime.timedelta(
					hours  = start_time.hour,
					minutes= start_time.minute,
				)
			else:
				self.start_time = datetime.datetime(
					year   = self.date.year,
					month  = self.date.month,
					day    = self.date.day,
					hour   = start_time.hour,
					minute = start_time.minute,
				)
		return self.start_time

	# stop_time can either indicate when the event ended
	_STOP_INITIALS     = ('s', 'e')
	# or how long it lasted
	_DURATION_INITIALS = ('d')
	def _parser_stop_time(self, s):
		"""
		after this initial parsing, the following cases are possible:
			- self.stop_time_type = "copy"
			  self.stop_time is str
				if stop_time is the special placeholder COPY_LAST_STOP_TIME
			- self.stop_time_type = "stop"
				if stop_time tells the final time
				- self.stop_time is a datetime object
					if self.date is a datetime object
				- self.stop_time is a timedelta object
					if self.date is str
			- self.stop_time_type = "duration"
			  self.stop_time is a timedelta object
				if stop_time tells the duration
		"""
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

		# get both the word before the brackets, and the value of the brackets
		extra_details = re.findall("(\\w+)\\s+\\((.*?)\\)", s)
		if not extra_details:
			# TODO: maybe make it an empy dict instead of None
			self.extra_details = None
		else:
			self.extra_details = dict(extra_details)

		return s

	@property
	def PARSERS(self):
		"""
		returns a list of parsers by order
		"""
		return [
			self._parser_date,
			self._parser_start_time,
			self._parser_stop_time,
			self._parser_group,
			self._parser_description,
		]

	def _format_date(self):
		if type(self.date) is str:
			return self.date
		else:
			return self.date.strftime("%Y/%m/%d")
	def _format_start_time(self):
		if type(self.start_time) is str:
			return self.start_time
		elif type(self.start_time) is datetime.timedelta:
			return int(self.start_time.total_seconds())
		else:
			return self.start_time.strftime("%H:%M")
	def _format_stop_time(self):
		days = "    "

		if type(self.stop_time) is str:
			hour = self.stop_time
		elif type(self.stop_time) is datetime.timedelta:
			hour = str(int(self.stop_time.total_seconds()))
		else:
			hour = self.stop_time.strftime("%H:%M")
			# check if a day has passed
			if get_ymd_tuple(self.start_time) != get_ymd_tuple(self.stop_time):
				days = "(+%d)" % ((self.stop_time - self.start_time).days + 1)
		return hour + ' ' + days

	def _format_group(self):
		return self.group
	def _format_description(self):
		return self.description

	#
	# second parse iteration
	#
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
	def reevaluate(self, p, n):
		"""
		reevaluates the start and stop times of this object
		this calls the second parsing functions
		p & n stands for previous & next items
			(I avoided calling 'n' "next" because it is a builtin python function)
		"""

		self._reevaluate_date(p, n)
		self._reevaluate_start_time(p, n)
		self._reevaluate_stop_time(p, n)

		if get_ymd_tuple(self.start_time) != get_ymd_tuple(self.date):
			print("[!] date & start_time mismatch!")
			print(self)
			import pdb; pdb.set_trace()

	def is_fully_parsed(self):
		"""
		checks whether every object has the type it is supposed to have
		"""
		return all([
			type(self.date) is datetime.datetime,
			type(self.start_time) is datetime.datetime,
			type(self.stop_time) is datetime.datetime,
			type(self.group) is str,
			type(self.description) is str,
			self.stop_time > self.start_time,
		])

	def is_in_date_range(self, start_date, end_date,
		include_by_start=True, include_by_stop=False):
		"""
		returns True if:
			The whole Data object               is contained within the date_range
			include_by_start && Data.start_time is contained within the date_range
			include_by_stop  && Data.stop_time  is contained within the date_range
		"""
		if (start_date <= self.start_time) and (self.stop_time <= end_date):
			return True
		if include_by_start and (start_date <= self.start_time <= end_date):
			return True
		if include_by_stop  and (start_date <= self.stop_time  <= end_date):
			return True
		return False


class DataFile(object):
	def __init__(self, path=None):
		self._path = path or self.file_path
		self.reload()

	def __repr__(self):
		return "%s : %s : %d items" % (
			self.__class__.__name__,
			self._path,
			len(self.data)
		)

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
				lambda x: DataItem(x),
				r
			)
		))

	def _reevaluate_data(self):
		# ignoring first and last, which doesnt have 'prev' and 'next' respectivly
		for i in range(len(self.data[1:-1])):
			self.data[i+1].reevaluate(self.data[i], self.data[i+2])

		# calling the last item, with its previous item
		self.data[-1].reevaluate(self.data[-2], None)

	def _validate_data(self):
		invalid_items = [i for i in self.data if not i.is_fully_parsed()]
		return invalid_items or True
		return all(x.is_fully_parsed() for x in self.data)

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

	@property
	def _data_range(self):
		return self.data[0].start_time, self.data[-1].stop_time



class DataFolder(object):
	def __init__(self, folder=DEFAULT_DATA_DIRECTORY):
		self._path = folder

		self._load_data_files()

	def _load_data_files(self):
		files = next(os.walk(self._path))[2]

		# each data file, in its constructor, loads its content
		self.data_files = [
			DataFile(os.path.join(self._path, i))
			for i in files
		]
		# sort the data files by date
		self.data_files = sorted(
			self.data_files,
			key=lambda df: df._data_range[1]
		)

		self.data = sum([i.data for i in self.data_files], [])

		# TODO
		newest_path = newest(self._path)
		self.data_file_latest = [
			i for i in self.data_files
			if i._path.endswith(newest_path)
		][0]
		self.data_latest = self.data_file_latest.data

	def reload(self):
		for i in self.data_files:
			i.reload()

	def _validate_data(self):
		invalid_items = []
		res = True
		for i in self.data_files:
			temp = i._validate_data()
			if type(temp) is list:
				invalid_items += temp
			else:
				res &= temp
		return invalid_items or res

