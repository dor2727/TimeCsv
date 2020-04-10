import datetime
import calendar

import operator
import itertools

from TimeCsv.time_utils import *

class Filter(object):
	def filter(self, data):
		raise NotImplemented

	def get_filtered_data(self, data):
		return list(itertools.compress(data, self.filter(data)))

	def __mod__(self, other):
		# verify input
		if type(other) is not list:
			raise ValueError("modulo not defined for filter and non-list object")
		if other[0].__class__.__name__ != "DataItem":
			raise ValueError("modulo is only defined for filter and a list of DataItem elements")

		return self.get_filtered_data(other)

	def __and__(self, other):
		return MultiFilter(self, other, "and")

	def __or__(self, other):
		return MultiFilter(self, other, "or")

	def __invert__(self):
		"""
		returns a Not Filter for this object
		syntax: ~obj
		"""
		return NotFilter(self)

	def __repr__(self):
		return self.__class__.__name__

class MultiFilter(Filter):
	"""docstring for MultiFilter"""
	def __init__(self, filter_1, filter_2, operation):
		self.filter_1 = filter_1
		self.filter_2 = filter_2

		self.operation = operation
		if operation.lower() == "and":
			self.operator = operator.and_
		elif operation.lower() == "or":
			self.operator = operator.or_
		else:
			raise ValueError("invalid operation! please use either \"and\" or \"or\"")

	def filter(self, data):
		return map(
			self.operator,
			self.filter_1.filter(data),
			self.filter_2.filter(data)
		)

	def __repr__(self):
		return f"({self.filter_1.__repr__()}) {self.operation} ({self.filter_2.__repr__()})"

	@property
	def selected_time(self):
		if hasattr(self.filter_1, "selected_time") and hasattr(self.filter_2, "selected_time"):
			return f"{self.filter_1.selected_time} {self.operation} {self.filter_2.selected_time}"
		elif hasattr(self.filter_1, "selected_time"):
			return self.filter_1.selected_time
		elif hasattr(self.filter_2, "selected_time"):
			return self.filter_2.selected_time
		else:
			return ''

class NotFilter(Filter):
	def __init__(self, filter_obj):
		self.filter_obj = filter_obj

	def filter(self, data):
		return map(
			operator.not_,
			self.filter_obj.filter(data),
		)

	def __repr__(self):
		return f"not ({self.filter_obj.__repr__()})"



# used for debug purpose
class TrueFilter(Filter):
	def filter(self, data):
		return [True] * len(data)
class FalseFilter(Filter):
	def filter(self, data):
		return [False] * len(data)


class DescriptionFilter(Filter):
	def __init__(self, string, case_sensitive=None, regex=False):
		self.case_sensitive = case_sensitive or False
		self.regex = regex

		if self.case_sensitive:
			self.string = string
		else:
			self.string = string.lower()

	def filter(self, data):
		if       self.regex and     self.case_sensitive:
			return [
				bool(re.findall(self.string, i.description))
				for i in data
			]

		elif     self.regex and not self.case_sensitive:
			return [
				bool(re.findall(self.string, i.description, re.I))
				for i in data
			]

		elif not self.regex and     self.case_sensitive:
			return [
				self.string in i.description
				for i in data
			]

		elif not self.regex and not self.case_sensitive:
			return [
				self.string in i.description.lower()
				for i in data
			]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.string})"

class GroupFilter(Filter):
	def __init__(self, string, case_sensitive=None, regex=False):
		self.case_sensitive = case_sensitive or True
		self.regex = regex

		if self.case_sensitive:
			self.string = string
		else:
			self.string = string.lower()

	def filter(self, data):
		if       self.regex and     self.case_sensitive:
			return [
				bool(re.findall(self.string, i.group))
				for i in data
			]

		elif     self.regex and not self.case_sensitive:
			return [
				bool(re.findall(self.string, i.group, re.I))
				for i in data
			]

		elif not self.regex and     self.case_sensitive:
			return [
				self.string in i.group
				for i in data
			]

		elif not self.regex and not self.case_sensitive:
			return [
				self.string in i.group.lower()
				for i in data
			]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.string})"

class FriendFilter(Filter):
	def __init__(self, friend, case_sensitive=False):
		self.case_sensitive = case_sensitive

		if self.case_sensitive:
			self.friend = friend
		else:
			self.friend = friend.lower()

	def filter(self, data):
		if self.case_sensitive:
			return [
				self.friend in i.friends
				for i in data
			]

		else: # not case_sensitive
			return [
				self.friend in map(str.lower, i.friends)
				for i in data
			]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.friend})"

class HasExtraDetailsFilter(Filter):
	def filter(self, data):
		return [
			bool(i.extra_details)
			for i in data
		]



# find str in either group or description
class StrFilter(Filter):
	def __init__(self, string, case_sensitive=None, regex=False):
		self._group       = GroupFilter(      string,
			case_sensitive=case_sensitive, regex=regex
		)
		self._description = DescriptionFilter(string,
			case_sensitive=case_sensitive, regex=regex
		)

		self.string = string
		self.case_sensitive = case_sensitive
		self.regex = regex

		self._multi = self._group | self._description

	def filter(self, data):
		return self._multi.filter(data)

	def __repr__(self):
		return self._multi.__repr__()


# auto classify which filter to use
class AutoFilter(Filter):
	def __init__(self, string, case_sensitive=None):
		regex = '\\' in string

		if regex:
			friends = False
		else:
			friends = find_friends_in_str(string)

		if not regex and friends:
			self._filter = FriendFilter(friends[0],
				case_sensitive=case_sensitive
			)

			for i in friends[1:]:
				self._filter |= FriendFilter(i,
					case_sensitive=case_sensitive
				)

		elif string.islower():
			self._filter = DescriptionFilter(string,
				case_sensitive=case_sensitive, regex=regex
			)
		elif string.istitle():
			self._filter = GroupFilter(string,
				case_sensitive=case_sensitive, regex=regex
			)
		else:
			self._filter = StrFilter(string,
				case_sensitive=case_sensitive, regex=regex
			)

	def filter(self, data):
		return self._filter.filter(data)

	def __repr__(self):
		return self._filter.__repr__()


# do not use this class directly
class TimeFilter(Filter):
	def filter(self, data):
		return [
			i.is_in_date_range(self.start_time, self.stop_time)
			for i in data
		]

	def __str__(self):
		return DATE_REPRESENTATION_PATTERN % (
			*get_ymd_tuple(self.start_time),
			*get_ymd_tuple(self.stop_time),
		)

	def __repr__(self):
		name = self.__class__.__name__
		start = self.start_time.strftime("%Y/%m/%d")
		stop = self.stop_time.strftime("%Y/%m/%d")
		return f"{name}({start} --> {stop})"

	@property
	def selected_time(self):
		raise NotImplemented
	

class TimeFilter_Days(TimeFilter):
	def __init__(self, days: int=7):
		"""
		amount of days to take
		1 means today only
		2 means today + yesterday
		8 means a week plus a day. E.g. from sunday to subday, inclusive
		"""
		self.days = days
		
		self.stop_time = datetime.datetime.now()
		self.start_time = get_midnight(
			self.stop_time
			 -
			# added the "minus 1" since taking today only means taking midnight of now
			# thus, we need to reduce a timedelta of 0 days when amount of days is 1
			datetime.timedelta(days=days-1)
		)

		self.selected_time

	def filter(self, data):
		return [
			i.is_in_date_range(self.start_time, self.stop_time)
			for i in data
		]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.days or 'today'})"

	@property
	def selected_time(self):
		return f"days ({self.days})"
	

class TimeFilter_Year(TimeFilter):
	def __init__(self, year: int=0):
		self.year = year or datetime.datetime.now().year
		
		self.start_time = datetime.datetime(self.year, 1,  1 )
		self.stop_time  = datetime.datetime(self.year, 12, 31)

	def filter(self, data):
		return [
			i.date.year == self.year
			for i in data
		]

	def __str__(self):
		return DATE_REPRESENTATION_PATTERN % (
			self.year, 1,  1,
			self.year, 12, 31
		)

	def __repr__(self):
		return f"{self.__class__.__name__}({self.year})"

	@property
	def selected_time(self):
		return f"year ({self.year})"

class TimeFilter_Month(TimeFilter):
	def __init__(self, month: int=0, year: int=0):
		"""
		if year==0: get the last occurence of that month
		else: get that specific month
		"""
		self.month = month or datetime.datetime.now().month
		if year == 0:
			now = datetime.datetime.now()
			if self.month > now.month:
				self.year = now.year - 1
			else:
				self.year = now.year
		else:
			self.year = year
		
		self.start_time = datetime.datetime(self.year, self.month, 1)
		self.stop_time  = datetime.datetime(self.year, self.month,
			calendar.monthrange(self.year, self.month)[1])

	def filter(self, data):
		return [
			i.date.year == self.year
			 and
			i.date.month == self.month
			for i in data
		]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.year}/{self.month})"

	@property
	def selected_time(self):
		return f"month ({self.year}/{self.month})"

class TimeFilter_DateRange(TimeFilter):
	def __init__(self, start_time, stop_time,
		include_by_start=True, include_by_stop=False):
		"""
		date is included if:
			The whole Data object               is contained within the date_range
			include_by_start && Data.start_time is contained within the date_range
			include_by_stop  && Data.stop_time  is contained within the date_range
		"""
		
		self.start_time = start_time
		self.stop_time  = stop_time

	def filter(self, data):
		return [
			i.is_in_date_range(self.start_time, self.stop_time,
				self.include_by_start, self.include_by_stop)
			for i in data
		]

	@property
	def selected_time(self):
		return "daterange"


class AutoTimeFilter(TimeFilter):
	"""
	input type:
		dict
			"year" = int or "current"
			"month" = int or "current"

			if only year - get the whole year
			if only month - get the last occurence of that month
			if both - get that specific month
		tuple
			(
				datetime start,
				datetime stop,
				bool start_inclusive optional,
				bool stop_inclusive optional
			)

		int
			get last n days
	"""
	def __init__(self, arg):
		self.arg = arg

		if type(arg) is dict:
			if "year" not in arg or type(arg["year"]) is not int:
				raise ValueError("Invalid input type")

			if "month" in arg:
				if type(arg["month"]) is not int:
					raise ValueError("Invalid input type")
				self._filter = TimeFilter_Month(*arg)
			else:
				self._filter = TimeFilter_Year(*arg)

		elif type(arg) is tuple:
			# verify input
			if len(arg) < 2 or len(arg) > 4:
				raise ValueError("Invalid input type")
			if type(arg[0]) is not datetime.datetime:
				raise ValueError("Invalid input type")
			if type(arg[1]) is not datetime.datetime:
				raise ValueError("Invalid input type")
			if len(arg) > 2 and type(arg[2]) is not bool:
				raise ValueError("Invalid input type")
			if len(arg) > 3 and type(arg[3]) is not bool:
				raise ValueError("Invalid input type")

			self._filter = TimeFilter_DateRange(*arg)
		elif type(arg) is int:
			self._filter = TimeFilter_Days(abs(int(arg)))
		else:
			raise ValueError("Unknown input type")

	def filter(self, data):
		return self._filter.filter(data)

	def __repr__(self):
		return self._filter.__repr__()

	@property
	def selected_time(self):
		return self._filter.selected_time

# __all__ = list(filter( lambda i: "Filter" in i, locals() ))
