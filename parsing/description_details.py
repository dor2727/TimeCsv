import re

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

		friends_list = self._combine_friends_list(self, found)

		# unique
		return ordered_unique(friends_list)

	def _get_all_friends(self, dataitem):
		found = []
		for pattern in self.PATTERN_EXTRACT:
			found += re.findall(pattern, dataitem.description)

		# search_at_beginning 
		if dataitem.group == "Friends":
			found += re.findall(f"^{PATTERN_NAMES_LIST}", dataitem.description)

		return found

	def _combine_friends_list(self, friends_list):
		# join all results into a big string
		friends_list = ' '.join(i[0] for i in friends_list)
		# remove 'and', and convert back into a list
		friends_list = re.sub("\\band\\b", '', friends_list)
		friends_list = friends_list.split()
		return friends_list

	@classmethod
	def strip(self, string):
		for pattern in self.PATTERN_STRIP:
			string = re.sub(pattern, '', string)
		return string.strip()

	# An extracted API for finding friends in a string without a dataitem
	@classmethod
	def extract_values_from_string(self, string):
		found = []
		for pattern in self.PATTERN_EXTRACT:
			found += re.findall(pattern, string)

		friends_list = self._combine_friends_list(self, found)

		# unique
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
