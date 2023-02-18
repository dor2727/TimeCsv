import re
from operator import itemgetter

from .consts import *
from ..utils import ordered_unique

class DescriptionDetailsParser(object):
	PATTERN_STRIP = None
	PATTERN_EXTRACT = None

	# this function requires the whole DataItem object
	@classmethod
	def extract_values(cls, dataitem):
		raise NotImplemented

	# this function requires only the description
	@classmethod
	def strip(cls, string):
		if isinstance(cls.PATTERN_STRIP, (str, re.Pattern)):
			return re.sub(cls.PATTERN_STRIP, '', string).strip()

		elif isinstance(cls.PATTERN_STRIP, list):
			for pattern in cls.PATTERN_STRIP:
				string = re.sub(pattern, '', string)
			return string.strip()

		else:
			raise NotImplemented

class DescriptionDetailsParser_ExtraDetails(DescriptionDetailsParser):
	PATTERN_STRIP   = EXTRA_DETAILS_PATTERN_STRIP
	PATTERN_EXTRACT = EXTRA_DETAILS_PATTERN_EXTRACT

	@classmethod
	def extract_values(cls, dataitem):
		try:
			extra_details = re.findall(cls.PATTERN_EXTRACT, dataitem.description)
		except:
			import ipdb; ipdb.set_trace()

		extra_details_dict = {
			k: v.split(EXTRA_DETAILS_SEPERATOR)
			for k,v in extra_details
		}

		return extra_details_dict

class DescriptionDetailsParser_Friends(DescriptionDetailsParser):
	PATTERN_STRIP   = FRIEND_PATTERN_STRIP + [FRIEND_PATTERN_TO_FRIENDS]
	PATTERN_EXTRACT = FRIEND_PATTERN_EXTRACT

	@classmethod
	def extract_values(cls, dataitem):
		found = cls._get_all_friends(dataitem)
		return cls._combine_and_order_friends_list(found)

	# An extracted API for finding friends in a string without a dataitem
	@classmethod
	def extract_values_from_string(cls, string):
		found = cls._get_friends_from_description(string)
		return cls._combine_and_order_friends_list(found)

	@classmethod
	def _get_friends_from_description(cls, description):
		found = []

		for pattern in cls.PATTERN_EXTRACT:
			found += re.findall(pattern, description)

		return found

	@staticmethod
	def _get_friends_from_group(dataitem):
		# search_at_beginning 
		if dataitem.group == "Friends":
			found = re.findall(f"^{PATTERN_NAMES_LIST}", dataitem.description)
		else:
			found = []

		return found

	@classmethod
	def _get_all_friends(cls, dataitem):
		return cls._get_friends_from_description(dataitem.description) + cls._get_friends_from_group(dataitem)

	@staticmethod
	def _combine_friends_list(friends_list):
		# get the first result from `re.findall`
		all_results = map(itemgetter(0), friends_list)

		all_results = map(REMOVE_AND, all_results)

		all_results_2d = map(str.split, all_results)
		return sum(all_results_2d, [])

	@classmethod
	def _combine_and_order_friends_list(cls, friends_list):
		friends_list = cls._combine_friends_list(found)
		return ordered_unique(friends_list)

class DescriptionDetailsParser_Location(DescriptionDetailsParser):
	PATTERN_STRIP   = PATTERN_LOCATION
	PATTERN_EXTRACT = PATTERN_LOCATION


	@classmethod
	def extract_values(cls, dataitem):
		return cls.extract_values_from_string(dataitem.description)

	@classmethod
	def strip(cls, string):
		string = re.sub(cls.PATTERN_STRIP, '', string)
		string = re.sub(PATTERN_LOCATION_THEIR_PLACE, '', string)
		return string.strip()

	# An extracted API for finding a location in a string without a dataitem
	@classmethod
	def extract_values_from_string(cls, string):
		if PATTERN_LOCATION_THEIR_PLACE in string:
			return "Their place"

		l = re.findall(cls.PATTERN_EXTRACT, string)
		if len(l) == 0:
			return None
		elif len(l) == 1:
			return l[0]
		else:
			print(f"[!] Multiple locations found: {l}")
			raise ValueError(f"Too many ({len(names)}) possible locations found")


class DescriptionDetailsParser_Vehicle(DescriptionDetailsParser):
	PATTERN_STRIP = VEHICLE_PATTERN_STRIP


	@classmethod
	def extract_values(cls, dataitem):
		return cls.extract_values_from_string(dataitem.description)

	# An extracted API for finding a location in a string without a dataitem
	@staticmethod
	def extract_values_from_string(string):
		for vehicle in VEHICLES:
			if f"by {vehicle}" in string:
				return vehicle
		return None

DETAIL_PARSERS = {
	"extra_details": DescriptionDetailsParser_ExtraDetails,
	"friends"      : DescriptionDetailsParser_Friends,
	"location"     : DescriptionDetailsParser_Location,
	"vehicle"      : DescriptionDetailsParser_Vehicle,
}
