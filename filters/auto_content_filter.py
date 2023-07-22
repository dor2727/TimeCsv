from pandas import DataFrame

from .content_filters import *
from ..parsing.description_details import	DescriptionDetailsParser_Friends     , \
											DescriptionDetailsParser_Location    , \
											DescriptionDetailsParser_Vehicle
from ..parsing.consts import GROUP_SEPERATOR


_PREFIX_NEGATIVE = ('~', '!')

def _preprocess_string(string: str) -> str:
	if string[0] in _PREFIX_NEGATIVE:
		exclude = True
		string = string[1:]
	else:
		exclude = False

	return string, exclude

_AUTO_FILTERS = (
	(
		filter_duration_from_str,
		lambda s: s[0] in ('<', '>')
	),

	(
		filter_friends_from_str,
		DescriptionDetailsParser_Friends.extract_values_from_string
	),
	(
		filter_location_from_str,
		DescriptionDetailsParser_Location.extract_values_from_string
	),
	(
		filter_vehicle_exact,
		DescriptionDetailsParser_Vehicle.extract_values_from_string
	),

	(
		filter_description_contains,
		str.islower
	),
	(
		filter_sub_groups_at_any_index,
		lambda s: s.startswith(GROUP_SEPERATOR)
	),
	(
		filter_sub_groups_from_str,
		lambda s: GROUP_SEPERATOR in s
	),
	(
		filter_main_group,
		lambda s: s[0].isupper()
	),
)

def filter_content_auto(df: DataFrame, string: str):
	string, exclude = _preprocess_string(string)

	for filter_function, filter_check in _AUTO_FILTERS:
		if filter_check(string):
			filtered = filter_function(df, string)

			if exclude:
				filtered = ~filtered

			return filtered

	# If all failed - default filter
	return (
		filter_main_group(df, string.capitalize())
		| filter_description_contains(df, string.lower())
	)
