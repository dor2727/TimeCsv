from .base_filters import ComplexFilter
from .content_filters import *
from .filter_utils import join_filters_with_or
from .time_filters import *
from ..parsing import 	DescriptionDetailsParser_Friends , \
						DescriptionDetailsParser_Location, \
						DescriptionDetailsParser_Vehicle

# find str in either group or description
class StrFilter(ComplexFilter):
	def __init__(self, string, case_sensitive=None, regex=None):
		self._group       = GroupFilter(      string,
			case_sensitive=case_sensitive, regex=regex
		)
		self._description = DescriptionFilter(string,
			case_sensitive=case_sensitive, regex=regex
		)

		self._filter = self._group | self._description

		self.string = string
		self.case_sensitive = case_sensitive
		self.regex = regex

# auto classify which filter to use
class AutoFilter(ComplexFilter):
	_not_filter_prefix = ('~', '!')

	def __init__(self, string, case_sensitive=None, force_regex=False):
		string, exclude, regex = self._preprocess_string(string, force_regex)

		if not self._try_to_set_filter_special_case(string, regex):
			self._set_filter_normal_case(string, regex)

		if exclude:
			self._filter = NotFilter(self._filter)

	def _preprocess_string(self, string, force_regex):
		# check for regex
		regex = ('\\' in string) or force_regex

		# check whether this will be a NotFilter
		if not regex and string[0] in self._not_filter_prefix:
			exclude = True
			string = string[1:]
		elif   regex and string[0] == '~':
			# '!' is a special char for regex, '~' is not, thus, only '~' is allowed for regex exclude
			exclude = True
			string = string[1:]
		else:
			exclude = False

		if not string:
			raise ValueError("AutoFilter got empty string")

		return string, exclude, regex

	def _try_to_set_filter_special_case(self, string, regex):
		if string[0] in ('<', '>'):
			self._filter = DurationFilter(string)
			return True

		# all of the following cases do not support regex
		if regex:
			return False

		friends = DescriptionDetailsParser_Friends.extract_values_from_string(string)
		if friends:
			self._filter = join_filters_with_or(
				FriendFilter(friend,
					case_sensitive=case_sensitive
				) for friend in friends
			)
			return True

		location = DescriptionDetailsParser_Location.extract_values_from_string(string)
		if location:
			self._filter = LocationFilter(location, case_sensitive=case_sensitive)
			return True

		vehicle = DescriptionDetailsParser_Vehicle.extract_values_from_string(string)
		if vehicle:
			self._filter = VehicleFilter(vehicle, case_sensitive=case_sensitive)
			return True

		return False

	def _set_filter_normal_case(self, string, regex):
		if string.islower():
			self._filter = DescriptionFilter(string,
				case_sensitive=case_sensitive, regex=regex
			)

		elif string[0].isupper():
			self._filter = GroupFilter(string,
				case_sensitive=case_sensitive, regex=regex
			)

		else:
			self._filter = StrFilter(string,
				case_sensitive=case_sensitive, regex=regex
			)


class AutoTimeFilter(BaseTimeFilter):
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
			self._verify_time_range_tuple(arg)
			self._filter = TimeFilter_DateRange(*arg)

		elif type(arg) is int:
			self._filter = TimeFilter_Days(abs(int(arg)))

		else:
			raise ValueError("Unknown input type")

	def _verify_time_range_tuple(self, time_range_tuple):
		# verify input
		if len(time_range_tuple) < 2 or len(time_range_tuple) > 4:
			raise ValueError("Invalid input type")
		if type(time_range_tuple[0]) is not datetime.datetime:
			raise ValueError("Invalid input type")
		if type(time_range_tuple[1]) is not datetime.datetime:
			raise ValueError("Invalid input type")
		if len(time_range_tuple) > 2 and type(time_range_tuple[2]) is not bool:
			raise ValueError("Invalid input type")
		if len(time_range_tuple) > 3 and type(time_range_tuple[3]) is not bool:
			raise ValueError("Invalid input type")
