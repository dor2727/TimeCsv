import os
import csv

from TimeCsv.consts import *
from TimeCsv.utils import *
from TimeCsv.parsing.parse_exception import ParseError


class DataItemParser(object):
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
	"""
	def __init__(self, items, file_name="Unknown", line="??"):
		# debug information
		self._file_name = file_name
		self._line = line

		if self._check_if_comment(items):
			return

		self._items = []
		for i in range(len(self.PARSERS)):
			self._items.append(
				self.PARSERS[i](items[i])
			)

	def __repr__(self):
		if self.is_comment:
			return "# A comment"

		return "%s : %s : %s : %-14s : %s" % (
			self._format_date(),
			self._format_start_time(),
			self._format_stop_time(),
			self._format_group(),
			self._format_description(),
		)


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

	def _format_error(self, text):
		return f"[!] {text} in file \"{self._file_name}\" : {self._line} : < {self} >"


	#
	# first parse iteration
	#
	def _parser_date(self, s):
		"""
		after this initial parsing, self.date will be:
			- str, if it was a special placeholder in the csv
			- datetime object, if it was a regular date value
		"""
		if s in SPECIAL_DATE_FORMATS:
			self.date = s
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
		if s in SPECIAL_START_TIME_FORMATS:
			self.start_time = s
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
		self.is_break = False

		if s == COPY_LAST_STOP_TIME:
			self.stop_time_type = "copy"
			self.stop_time = COPY_LAST_STOP_TIME
		else:
			if s[0] in STOP_TIME_INITIALS_STOP:
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
			elif s[0] in STOP_TIME_INITIALS_DURATION:
				self.stop_time_type = "duration"
				duration = datetime.datetime.strptime(s[1:], "%H:%M")
				# it will be added to self.start_time at self._reevaluate_start_time
				self.stop_time = datetime.timedelta(
					hours=duration.hour,
					minutes=duration.minute,
				)

				if s[0] in STOP_TIME_INITIALS_BREAK:
					self.is_break = True
			else:
				# setting the stop_time for the debug message
				self.stop_time = s
				raise ParseError(self._format_error(f"Invalid stop_initial encountered: \'{s[0]}\'"))

		return self.stop_time
	def _parser_group(self, s):
		self.group = s
		return s
	def _parser_description(self, s):
		self.description = s
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
		if not hasattr(self, "date"):
			return "????/??/??"

		if type(self.date) is str:
			return self.date
		else:
			return self.date.strftime("%Y/%m/%d")
	def _format_start_time(self):
		if not hasattr(self, "start_time"):
			return "??:??"

		if type(self.start_time) is str:
			return self.start_time
		elif type(self.start_time) is datetime.timedelta:
			return int(self.start_time.total_seconds())
		else:
			return self.start_time.strftime("%H:%M")
	def _format_stop_time(self):
		if not hasattr(self, "stop_time"):
			return "??:??     "

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
		return getattr(self, "group", "???")
	def _format_description(self):
		return getattr(self, "description", "???")

	#
	# second parse iteration
	#
	def _reevaluate_date(self, prev, next=None):
		if type(self.date) is str:
			if self.date == COPY_LAST_DATE:
				self.date = prev.date
			elif self.date == ADD_LAST_DATE:
				self.date = prev.date + datetime.timedelta(days=1)

		if type(self.start_time) is datetime.timedelta:
			try:
				self.start_time = self.date + self.start_time
			except Exception as exc:
				raise ParseError(self._format_error(f"Error setting start_time in `_reevaluate_date`")) from exc

		if type(self.stop_time) is datetime.timedelta and self.stop_time_type == "stop":
			try:
				self.stop_time = self.date + self.stop_time
			except Exception as exc:
				raise ParseError(self._format_error(f"Error setting stop_time in `_reevaluate_date`")) from exc
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
			raise ParseError(self._format_error(f"date & start_time mismatch"))

	def is_fully_parsed(self):
		"""
		checks whether every object has the type it is supposed to have
		"""
		return all([
			type(self.date       ) is datetime.datetime,
			type(self.start_time ) is datetime.datetime,
			type(self.stop_time  ) is datetime.datetime,
			type(self.group      ) is str,
			type(self.description) is str,
			self.stop_time > self.start_time,
		])
