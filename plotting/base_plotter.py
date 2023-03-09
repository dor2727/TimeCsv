from collections import namedtuple
from collections.abc import Collection
from dataclasses import dataclass
from pandas import DataFrame

from ..statistics import Statistics


class FilteredDF:
	def __init__(self, filtered_df: DataFrame, group_name: str):
		self.df = filtered_df
		self.group_name = group_name

		self.statistics = Statistics(self.df)


class BasePlotter:
	def __init__(
		self,
		df: DataFrame,
		groups: "Callable[[df], list] | list",
		filter_by_group: "Callable[[df, group], df]"
	):
		self.df = df

		self.group_names = self._get_groups(groups)

		self.filtered_dfs = [
			FilteredDF(
				self.df[filter_by_group(self.df, group)],
				group
			)
			for group in self.group_names
		]

	def _get_groups(self, groups: "Callable[[df], list] | list"):
		if callable(groups):
			groups = groups(self.df)

		if not isinstance(groups, Collection):
			raise ValueError(f"The groups given should be a collection. {groups.__class__.__name__} given")

		return groups

	@property
	def max_group_name_length(self):
		return max(map(len, self.group_names))
