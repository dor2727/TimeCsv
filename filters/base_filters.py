"""
Filters are objects which get the data (as a list of DataItems), and returns only the relevant DataItems.

Each Filter object must implement a "filter" method.
	def filter(self, data):

	the return value is a list of boolean values.
	True  means "include this item"
	False means "exclude this item"

The reasoning behind returning a boolean list is for chaining Filters:
Logical operations, such as "and" and "or" may be applied in the following way:
	all_filters = (filter_1 & filter_2) | filter_3
Additionally, there is NotFilter, which reverses the value of the filter.
	not_filter_1 = ~filter_1
	not_filter_1 = NotFilter(filter_1)

After creating the required filter, it is used in the following way:
	filtered_data = filter_instance.get_filtered_data(list_of_data_items)
	# alternatively
	filtered_data = filter_instance % list_of_data_items

The availabe filters can be grouped into 2 categories:
Data Filters:
	they filter by the content of the DataItem

	- Description
	- Group
	- Friend
	- Has Extra Details
	- Duration

	- Str
		finds an str either in the Description or in the Group
	- Auto
		automatically determines whether to use Description, Group, Friend, or Duration
		mainly used for CLI, since the user input is not known in advance.

Time Filters:
	they filter by the date of the DataItem

	- Days
		returns items from the last N days (including today)
	- Today
		Days(1)
	- This Week
		Days(7)
	- Year
	- Month
	- DateRange
		gets a tuple of 2 Datetime objects, and returns objects which take place between the 2 Datetime objects
	- Auto
		automatically determines whether to use Days, DateRange, Year, or Month

"""

import datetime
import calendar

import operator
import itertools

from TimeCsv.utils import *

class Filter(object):
	def filter(self, data):
		raise NotImplemented

	def get_filtered_data(self, data):
		return list(itertools.compress(data, self.filter(data)))

	def get_selected_time(self):
		return getattr(self, "_selected_time", "All time")

	def __mod__(self, other):
		# verify input
		if type(other) is not list:
			raise ValueError("modulo not defined for filter and non-list object")

		# before the following check, verigy that the list is not empty:
		if len(other) == 0:
			# return the same thing, rather than an empty list, since `other` may be a tuple or something
			return other

		# Should check all the items, but there is currently no such case of a list with mixed types
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
		elif operation.lower() == "xor":
			self.operator = operator.xor
		else:
			raise ValueError("invalid operation! please use either \"and\", \"or\", or \"xor\"")

	def filter(self, data):
		return map(
			self.operator,
			self.filter_1.filter(data),
			self.filter_2.filter(data)
		)

	def __repr__(self):
		return f"({self.filter_1.__repr__()}) {self.operation} ({self.filter_2.__repr__()})"

	@property
	def _selected_time(self):
		if hasattr(self.filter_1, "_selected_time") and hasattr(self.filter_2, "_selected_time"):
			return f"({self.filter_1._selected_time} {self.operation} {self.filter_2._selected_time})"
		elif hasattr(self.filter_1, "_selected_time"):
			return self.filter_1._selected_time
		elif hasattr(self.filter_2, "_selected_time"):
			return self.filter_2._selected_time
		else:
			return 'All time'

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

class LocationFilter(Filter):
	def __init__(self, location, case_sensitive=False):
		self.case_sensitive = case_sensitive

		if self.case_sensitive:
			self.location = location
		else:
			self.location = location.lower()

	def filter(self, data):
		if self.case_sensitive:
			return [
				self.location == i.location
				for i in data
			]

		else: # not case_sensitive
			return [
				self.location in i.location.lower()
				for i in data
				if i.location
			]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.location})"

class HasExtraDetailsFilter(Filter):
	def filter(self, data):
		return [
			bool(i.extra_details)
			for i in data
		]

class DurationFilter(Filter):
	def __init__(self, string):
		if   type(string) is str and string[0] == '<':
			self._action = "maximum"
			self.seconds = self._int(string[1:])
		elif type(string) is str and string[0] == '>':
			self._action = "minumum"
			self.seconds = self._int(string[1:])
		else: # default
			self._action = "maximum"
			self.seconds = self._int(string)

	def _int(self, string):
		# the input may be 100.0
		return int(string.split('.')[0])

	def filter(self, data):
		if self._action == "maximum":
			return [
				int(i) <= self.seconds
				for i in data
			]
		elif self._action == "minumum":
			return [
				int(i) >= self.seconds
				for i in data
			]
		else:
			raise ValueError("Invalid action")

	def __repr__(self):
		return f"{self.__class__.__name__}({self._action} {self.seconds} seconds)"


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
	not_filter_prefix = ('~', '!')

	def __init__(self, string, case_sensitive=None, force_regex=False):
		# check for regex
		regex = ('\\' in string) or force_regex

		# check whether this will be a NotFilter
		if not regex and string[0] in self.not_filter_prefix:
			exclude = True
			string = string[1:]
		elif   regex and string[0] == '~':
			# '!' is a special char for regex, '~' is not, thus, only '~' is allowed for regex exclude
			exclude = True
			string = string[1:]
		else:
			exclude = False

		# extract friends
		if regex:
			friends = False
		else:
			friends = find_friends_in_str(string)

		if not string:
			raise ValueError("AutoFilter got empty string")

		elif not regex and friends:
			self._filter = FriendFilter(friends[0],
				case_sensitive=case_sensitive
			)

			for i in friends[1:]:
				self._filter |= FriendFilter(i,
					case_sensitive=case_sensitive
				)

		elif string[0] in ('<', '>'):
			self._filter = DurationFilter(string)
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

		if exclude:
			self._filter = NotFilter(self._filter)

	def filter(self, data):
		return self._filter.filter(data)

	def __repr__(self):
		return self._filter.__repr__()


# do not use this class directly - it is a meta class
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
	def _selected_time(self):
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

	def filter(self, data):
		return [
			i.is_in_date_range(self.start_time, self.stop_time)
			for i in data
		]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.days or 'today'})"

	@property
	def _selected_time(self):
		return f"days ({self.days})"

class TimeFilter_Today(TimeFilter_Days):
	def __init__(self):
		super().__init__(days=1)
	def __repr__(self):
		return f"{self.__class__.__name__}"
class TimeFilter_ThisWeek(TimeFilter_Days):
	def __init__(self):
		super().__init__(days=7)
	def __repr__(self):
		return f"{self.__class__.__name__}"


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
	def _selected_time(self):
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
	def _selected_time(self):
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

		self.start_time       = start_time
		self.stop_time        = stop_time
		self.include_by_start = include_by_start
		self.include_by_stop  = include_by_stop

	def filter(self, data):
		return [
			i.is_in_date_range(self.start_time, self.stop_time,
				self.include_by_start, self.include_by_stop)
			for i in data
		]

	@property
	def _selected_time(self):
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
	def _selected_time(self):
		return self._filter._selected_time

# __all__ = list(filter( lambda i: "Filter" in i, locals() ))


def join_filters_with_or(l):
	# check if list is empty
	l = list(filter(bool, l))
	if not l:
		return None

	f = l[0]
	for i in l[1:]:
		f |= i

	return f

def join_filters_with_and(l):
	l = list(filter(bool, l))
	# check if list is empty
	if not l:
		return None

	f = l[0]
	for i in l[1:]:
		f &= i

	return f

def get_named_filter(name, args=None):
	if name == "today":
		if args is None:
			return TimeFilter_Days(1)
		elif type(args) is int:
			return TimeFilter_Days(args)
		else:
			return TimeFilter_Days(*args)

	elif name == "yesterday":
		stop_time  = get_midnight( datetime.datetime.now() )
		start_time = get_midnight(
			stop_time
			 -
			datetime.timedelta(days=1)
		)

		return TimeFilter_DateRange( start_time, stop_time )

	elif name == "week":
		return TimeFilter_Days(7)

	elif name == "last_week":
		today = datetime.datetime.now()

		if WEEK_STARTS_AT_SUNDAY:
			weekday = today.weekday() + WEEK_STARTS_AT_SUNDAY
			if weekday == 7:
				weekday = 0
		else:
			weekday = today.weekday()
		this_sunday = get_midnight(today - datetime.timedelta(days=weekday))
		prev_sunday = this_sunday - datetime.timedelta(days=7)

		return TimeFilter_DateRange( prev_sunday, this_sunday )

	elif name == "month":
		if args is None:
			return TimeFilter_Month()
		elif type(args) is int:
			return TimeFilter_Month(args)
		else:
			return TimeFilter_Month(*args)

	elif name == "year":
		if args is None:
			return TimeFilter_Year()
		elif type(args) is int:
			return TimeFilter_Year(args)
		else:
			return TimeFilter_Year(*args)

	elif name == "all":
		return TrueFilter()

	else:
		return None
	