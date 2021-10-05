import re

from TimeCsv.statistics.base_statistics import DetailedStatsFiltered
from TimeCsv.filters import GroupFilter
from TimeCsv.consts import PATTERN_NAMES_LIST, PATTERN_LOCATION


class DetailedStats_Group(DetailedStatsFiltered):
	def __init__(
		self, data, group_name=None,
		time_filter=None, grouping_method="time", sorting_method="by_value",
		**filter_obj_kwargs,
	):
		self._set_filter_obj(group_name, **filter_obj_kwargs)

		super().__init__(data, self._filter_obj, time_filter, grouping_method, sorting_method)


	def _set_filter_obj(self, group_name, **filter_obj_kwargs):
		self._group_name = getattr(self, "_group_name", group_name)

		if self._group_name is None:
			raise ValueError("DetailedStats_Group received None as group name")

		print(f"filter_obj_kwargs: {filter_obj_kwargs}")
		self._filter_obj = GroupFilter(self._group_name, **filter_obj_kwargs)
		return self._filter_obj


	def _get_titles(self):
		titles = set()

		for i in self.data:
			t = self._strip(i.description)
			if not t:
				print(f"empty description for: {i}")
			titles.add(t)

		# return a list, sorted alphabetically
		self._titles = sorted(titles)
		return self._titles

	def _get_items_of_title(self, title):
		return list(filter(
			lambda i: title == self._strip(i.description),
			self.data
		))


	# todo
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
	def _strip(self, s):
		for r in self.STRIPPING_REGEX:
			s = re.sub(r, '', s)
		return s.strip()


class DetailedStats_Games(DetailedStats_Group):
	_group_name = "Gaming"

class DetailedStats_Youtube(DetailedStats_Group):
	_group_name = "Youtube"

class DetailedStats_Life(DetailedStats_Group):
	_group_name = "Life"

class DetailedStats_Read(DetailedStats_Group):
	_group_name = "Read"
