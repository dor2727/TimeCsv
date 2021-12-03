import os
import re
import csv

from TimeCsv.utils import *
from TimeCsv.parsing.consts import *
from TimeCsv.parsing.dataitem_parser     import DataItemParser
from TimeCsv.parsing.description_details import DETAIL_PARSERS
from TimeCsv.parsing.parse_exception     import ParseError


class DataItem(DataItemParser):
	"""
	exported functions:
		__int__:
			return the duration in seconds
		__add__:
			casting to int, and adding the durations
		__getitem__:
			return the items in the csv order
		__repr__

		friends:
			return a list of friends which were in the activity
		location:
			return a string of the location of the activity
		vehicle:
			return a string of the vehicle used

		reevaluate:
			used for calling 2nd parsing functions
		is_fully_parsed:
			checks whether this object has finished parsing, and is in a valid state
		is_in_date_range:
			checks whether this object is contained within a date range
	"""
	def __init__(self, items, file_name="Unknown", line="??"):
		super().__init__(items, file_name, line)
		
		if not self.is_comment:
			self._process_description_details()

	def _process_description_details(self):
		for k, v in DETAIL_PARSERS.items():
			setattr(self, k, v.extract_values(self))

	@property
	def description_stripped(self):
		description = self.description

		for k, v in DETAIL_PARSERS.items():
			description = v.strip(description)

		return description



	# exported functions
	def __getitem__(self, n):
		return self._items[n]


	# return total event time in seconds
	def __int__(self):
		return int( (self.stop_time - self.start_time).total_seconds() )

	# when __add__ is called (usually by calling `sum` on a list of DataItems), cast to int
	def __add__(self, other):
		if type(other) is DataItem:
			return int(self) + int(other)
		elif type(other) is int:
			return int(self) + other
		else:
			return NotImplemented
	def __radd__(self, other):
		if type(other) is DataItem:
			return int(self) + int(other)
		elif type(other) is int:
			return int(self) + other
		else:
			return NotImplemented

	# Compares the date of 2 DataItems
	def __lt__(self, other):
		return self.stop_time <  other.start_time
	def __le__(self, other):
		return self.stop_time <= other.start_time
	def __ge__(self, other):
		return self.start_time >= other.stop_time
	def __gt__(self, other):
		return self.start_time >  other.stop_time


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
	def __init__(self, path):
		self._path = path
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
		self._create_locations_list()

	def _load_data(self, path):
		handle = open(
			os.path.expandvars(
				os.path.expanduser(
					path
				)
			)
		)
		r = csv.reader(handle)

		try:
			self.headers = next(r)
		except StopIteration:
			self.empty = True

		self.data = list(filter(
			# filter out comment lines
			lambda x: not x.is_comment,
			map(
				# parse each line
				# obj is the output of enumerate - obj[0] is index, obj[1] is value
				lambda obj: DataItem(
					obj[1],
					file_name=self._path,
					line=obj[0],
				),
				enumerate(r)
			)
		))
		handle.close()

	def _reevaluate_data(self):
		# Ignoring empty files
		if len(self.data) < 2:
			return

		# ignoring first and last, which doesnt have 'prev' and 'next' respectivly
		for i in range(len(self.data[1:-1])):
			self.data[i+1].reevaluate(self.data[i], self.data[i+2])

		# calling the last item, with its previous item
		self.data[-1].reevaluate(self.data[-2], None)

	def _create_titles(self):
		# iterate every item in the data, collect its group into a unique list
		self.titles = list(set(i.group for i in self.data))
		self.titles.sort()

	def _create_friends_list(self):
		all_friends = sum((i.friends for i in self.data), [])

		self.friends_histogram = counter(all_friends)
		# counter object is a list of tuples (name, amount)
		self.friends_histogram.sort(key=lambda x:x[1], reverse=True)

		self.friends = [i[0] for i in self.friends_histogram]

	def _create_locations_list(self):
		all_locations = [i.location for i in self.data if i.location]

		self.locations_histogram = counter(all_locations)
		# counter object is a list of tuples (name, amount)
		self.locations_histogram.sort(key=lambda x:x[1], reverse=True)

		self.locations = [i[0] for i in self.locations_histogram]

	def _validate_data(self):
		invalid_items = [i for i in self.data if not i.is_fully_parsed()]
		return invalid_items or True

	def __getitem__(self, n):
		return self.data[n]

	@property
	def _data_range(self):
		if self.data:
			return self.data[0].start_time, self.data[-1].stop_time
		else:
			return NULL_DATE, NULL_DATE


class DataFolder(object):
	def __init__(self, folder=DEFAULT_DATA_DIRECTORY, recursive=True):
		self._path = folder
		self._recursive = recursive

		self._load_data_files()
		self._load_data()

	def __repr__(self):
		return "%s : %s : %d files : %d items" % (
			self.__class__.__name__,
			self._path,
			len(self.data_files),
			len(self.data)
		)

	def _get_all_data_files(self):
		self.data_files = []

		for folder_path, folders, files in os.walk(self._path):
			for file_name in files:
				# remove files starting with either '.' or '_':
				if file_name[0] == '.' or file_name[0] == '_':
					continue

				self.data_files.append(
					DataFile(
						os.path.join(folder_path, file_name)
					)
				)

			if not self._recursive:
				break

		# sort the data files by date
		self.data_files = sorted(
			self.data_files,
			key=lambda df: df._data_range[1]
		)


	def _load_data_files(self):
		self._get_all_data_files()

		self.data_file_latest = self.data_files[-1]
		self.data_latest = self.data_file_latest.data

	def _load_data(self):
		self.data      =          sum([i.data      for i in self.data_files], [])
		self.friends   = list(set(sum([i.friends   for i in self.data_files], [])))
		self.locations = list(set(sum([i.locations for i in self.data_files], [])))


	def __getitem__(self, n):
		return self.data[n]

	def reload(self):
		for i in self.data_files:
			i.reload()

		self._load_data()

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
