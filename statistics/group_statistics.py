import re

from TimeCsv.statistics.base_statistics import DetailedStats
from TimeCsv.consts import PATTERN_NAMES_LIST, PATTERN_LOCATION

class FilteredGroupedStats(DetailedStats):
	STRIPPING_REGEX = [
		# brackets
		" ?\\(.*?\\)",
		# friends
		" ?with %s" % PATTERN_NAMES_LIST,
		" ?for %s"  % PATTERN_NAMES_LIST,
		" ?to %s"   % PATTERN_NAMES_LIST,
		# at location
		PATTERN_LOCATION,

		# specific patterns
		" ?to friends"
	]

	def __init__(self, data, filter_obj, **kwargs):
		super().__init__(data, **kwargs)

		self._filter_obj = filter_obj

		self._initialize_data()

	def _initialize_data(self):
		self._original_data = self.data
		self.data = self._filter_obj % self.data

	def _strip(self, s):
		for r in self.STRIPPING_REGEX:
			s = re.sub(r, '', s)
		return s.strip()

	def _get_headers(self):
		# get all headers
		headers = set()

		for i in self.data:
			h = self._strip(i.description)
			if not h:
				print("empty description for: %s" % i)
			headers.add(h)

		# return a list, sorted alphabetically
		self._headers = sorted(headers)
		return self._headers

	def _get_filtered_data_per_header(self, header):
		return list(filter(
			lambda i: header == self._strip(i.description),
			self.data
		))

class GroupGroupedStats(FilteredGroupedStats):
	"""
	requires:
		self._category_name
	"""
	def __init__(self, data, category_name=None, **kwargs):
		self._category_name = getattr(self, "_category_name", category_name)

		filter_obj = GroupFilter(self._category_name)

		super().__init__(data, filter_obj, **kwargs)


class GroupedStats_Games(GroupGroupedStats):
	_category_name = "Gaming"

class GroupedStats_Youtube(GroupGroupedStats):
	_category_name = "Youtube"

class GroupedStats_Life(GroupGroupedStats):
	_category_name = "Life"

class GroupedStats_Read(GroupGroupedStats):
	_category_name = "Read"
