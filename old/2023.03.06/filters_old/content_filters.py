import operator

from .base_filters import Filter
from .filter_utils import find_string_in_string, find_string_in_list
from ..utils  import convert_to_case_sensitive

def _set_default_value(value: bool|None, default_value):
	if type(value) is bool:
		return value
	else:
		return default_value

# do not use this class directly - it is an abstract class
class BaseContentFilter(Filter):
	def __init__(self, string_to_find, case_sensitive=None, regex=None):
		self.case_sensitive = _set_default_value(case_sensitive, True)
		self.regex          = _set_default_value(regex         , False)

		self.string_to_find = convert_to_case_sensitive(string_to_find, self.case_sensitive)

	def __repr__(self):
		return f"{self.__class__.__name__}({self.string_to_find})"

	def _find_string_in_string(self, string_to_search_in, string_to_find=None):
		return find_string_in_string(
			string_to_find or self.string_to_find,
			string_to_search_in,
			self.regex,
			self.case_sensitive
		)

	def _find_string_in_list(self, list_to_search_in, string_to_find=None):
		return find_string_in_list(
			string_to_find or self.string_to_find,
			list_to_search_in,
			self.regex,
			self.case_sensitive
		)

#
# Desscription
#
class DescriptionFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return self._find_string_in_string(item.description)

#
# Group
#
class GroupFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return self._find_string_in_string(item.group)

#
# Friend
#
class FriendFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return self._find_string_in_list(item.friends)

#
# Location
#
class HasLocationFilter(Filter):
	def _filter_single_item(self, item):
		return bool(item.location)

class LocationFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return (
			bool(item.location)
			and
			self._find_string_in_string(item.location)
		)

#
# Vehicle
#
class HasVehicleFilter(Filter):
	def _filter_single_item(self, item):
		return bool(item.vehicle)

class VehicleFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return (
			bool(item.vehicle)
			and
			self._find_string_in_string(item.vehicle)
		)

#
# Extra Details
#
class HasExtraDetailsFilter(Filter):
	def _filter_single_item(self, item):
		return bool(item.extra_details)

# Filters whether there is a specific extra_details key in the DataItem
class ExtraDetailsFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return (
			bool(item.extra_details)
			and
			# `item.extra_details` is a dict, but it can both be iterated over and has `in`
			self._find_string_in_list(item.extra_details)
		)

# Filters whether there is a specific extra_details value to a certain key in the DataItem
class ExtraDetailsValueFilter(BaseContentFilter):
	def __init__(self, string_to_find, extra_details_name, case_sensitive=False, regex=False):
		super().__init__(string_to_find, case_sensitive, regex)

		self.extra_details_name = convert_to_case_sensitive(extra_details_name, self.case_sensitive)

	def _filter_single_item(self, item):
		return (
			bool(item.extra_details)
			and
			self._find_string_in_list(item.extra_details, self.extra_details_name)
			and
			self._find_string_in_list(item.extra_details[self.extra_details_name])
		)

#
# Duration
#
_OPERATOR_MAP = {
	"maximum": operator.ge,
	"minimum": operator.le,
}
class DurationFilter(Filter):
	def __init__(self, string):
		if   type(string) is str and string[0] == '<':
			self._action = "maximum"
			self.seconds = self._int(string[1:])
		elif type(string) is str and string[0] == '>':
			self._action = "minimum"
			self.seconds = self._int(string[1:])
		else: # default
			self._action = "maximum"
			self.seconds = self._int(string)

		try:
			self._operator = _OPERATOR_MAP[self._action]
		except KeyError as exc:
			allowed_operations = ", ".join(map("\"{}\"",format, _OPERATOR_MAP))
			raise ValueError(f"invalid operation! please use either {allowed_operations}") from exc


	def _int(self, string):
		# the input may be 100.0
		return int(float(string))

	def _filter_single_item(self, item):
		return self._operator(self.seconds, int(item))

	def __repr__(self):
		return f"{self.__class__.__name__}({self._action} {self.seconds} seconds)"

