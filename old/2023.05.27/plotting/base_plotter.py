from collections import namedtuple
from collections.abc import Collection
from dataclasses import dataclass
from pandas import DataFrame

from .consts import SortingMethods

# from ..statistics import Statistics


class FilteredDF:
	def __init__(self, filtered_df: DataFrame, group_name: str):
		self.df = filtered_df
		self.group_name = group_name

		self.statistics = Statistics(self.df)


def filter_by_group_and_remove_none(filter_by_group, df: DataFrame, group: str):
	return df[ filter_by_group(df, group).astype(bool) ]

class BasePlotter:
	def __init__(
		self,
		df: DataFrame,
		sorting_method: SortingMethods,
		groups: "Callable[[df], list] | list",
		filter_by_group: "Callable[[df, group], df]"
	):
		self.df = df
		self.sorting_method = sorting_method

		self.group_names = self._get_groups(groups)

		self.filtered_dfs = [
			FilteredDF(
				filter_by_group_and_remove_none(filter_by_group, self.df, group),
				group
			)
			for group in self.group_names
		]

	def _get_groups(self, groups: "Callable[[df], list] | list"):
		if callable(groups):
			groups = groups(self.df)

		if not isinstance(groups, Collection):
			raise ValueError(f"The groups given should be a collection. {groups.__class__.__name__} given")

		groups = list(groups)

		if None in groups:
			groups.remove(None)

		return groups

	@property
	def max_group_name_length(self):
		return max(map(len, self.group_names))
