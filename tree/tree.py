from typing import Type
from collections.abc import Iterable
from pandas import DataFrame
import numpy as np

from .title_types import *
from ..filters import *
from ..grouping import *

def create_tree(df: DataFrame) -> Tree:
	return CreateTree_MainGroup(df)()

def flatten_tree(t: Tree) -> list[Node]:
	all_nodes = []
	for value in t.values():
		all_nodes.append(value)
		all_nodes.extend(flatten_tree(value.sub_trees))
	return all_nodes


class CreateTree:
	NODE_VALUE_TYPE: Type[Title]

	def __init__(self, df: DataFrame, previous_path: NodePath=None):
		self.df = df
		self.previous_path = previous_path or ()

	def __call__(self) -> Tree:
		return {
			node.path[-1] : node
			for node in self._iterate_nodes()
		}

	def _get_all_titles(self) -> list[Title]:
		raise NotImplementedError

	def _filter_by_title(self, title: Title) -> DataFrame:
		raise NotImplementedError

	def _create_sub_tree(self, filtered_df: DataFrame, path: NodePath) -> Tree:
		if hasattr(self, "CreateSubTree"):
			return self.CreateSubTree(filtered_df, path)

		raise NotImplementedError

	def _create_node_value(self, title: Title) -> Title:
		if hasattr(self, "NODE_VALUE_TYPE"):
			return self.NODE_VALUE_TYPE(title)

		raise NotImplementedError

	def _create_node(self, title: Title) -> Node:
		node_value = self._create_node_value(title)
		node_path = self.previous_path + (node_value,)

		filtered_df = self._filter_by_title(title)
		sub_trees = self._create_sub_tree(filtered_df, node_path)

		return Node(node_path, filtered_df, sub_trees)

	def _iterate_nodes(self) -> Iterable[Node]:
		for title in self._get_all_titles():
			yield self._create_node(title)

class CreateTree_ExtraDetailsValue(CreateTree):
	NODE_VALUE_TYPE = ExtraDetailsValue

	def __init__(self, df: DataFrame, previous_path: NodePath, extra_details_key: str):
		super().__init__(df, previous_path)
		self.extra_details_key = extra_details_key

	def _get_all_titles(self) -> list[Title]:
		return get_all_extra_details_values(self.df, self.extra_details_key)

	def _filter_by_title(self, title: Title) -> DataFrame:
		return self.df[ filter_has_extra_details_value_exact(self.df, self.extra_details_key, title) ]

	def _create_sub_tree(self, filtered_df: DataFrame, path: NodePath) -> Tree:
		return {}

class CreateTree_ExtraDetailsKey(CreateTree):
	NODE_VALUE_TYPE = ExtraDetailsKey

	def _get_all_titles(self) -> list[Title]:
		return get_all_extra_details_keys(self.df)

	def _filter_by_title(self, title: Title) -> DataFrame:
		return self.df[ filter_has_extra_details_key(self.df, title) ]

	def _create_sub_tree(self, filtered_df: DataFrame, path: NodePath) -> Tree:
		extra_details_key = str(path[-1])
		return CreateTree_ExtraDetailsValue(filtered_df, path, extra_details_key)()

class CreateTree_Description(CreateTree):
	NODE_VALUE_TYPE = Description

	def _get_all_titles(self) -> list[Title]:
		return get_all_description(self.df)

	def _filter_by_title(self, title: Title) -> DataFrame:
		return self.df[ filter_description_exact(self.df, title) ]

	def _create_sub_tree(self, filtered_df: DataFrame, path: NodePath) -> Tree:
		return CreateTree_ExtraDetailsKey(filtered_df, path)()

class CreateTree_SubGroup(CreateTree):
	NODE_VALUE_TYPE = SubGroup

	def __init__(self, df: DataFrame, previous_path: NodePath, sub_group_level: int=1):
		super().__init__(df, previous_path)
		self.sub_group_level = sub_group_level

	def __call__(self):
		if self._is_end_of_sub_group():
			# proxy the call to CreateTree_Description
			return CreateTree_Description(self.df, self.previous_path)()
		else:
			return super().__call__()

	def _is_end_of_sub_group(self):
		all_sub_groups = self._get_all_titles()

		return (
			    len(all_sub_groups) == 1
			and isinstance(all_sub_groups[0], float)
			and np.isnan(all_sub_groups[0])
		)

	def _get_all_titles(self) -> list[Title]:
		return get_all_sub_groups_at_index(self.df, self.sub_group_level)

	def _filter_by_title(self, title: Title) -> DataFrame:
		return self.df[ filter_group_at_index(self.df, title, self.sub_group_level) ]

	def _create_sub_tree(self, filtered_df: DataFrame, path: NodePath) -> Tree:
		return self.__class__(filtered_df, path, self.sub_group_level+1)()

	def _create_node_value(self, title: Title) -> Title:
		if isinstance(title, float) and np.isnan(title):
			node_value = NoneSubGroup()
		else:
			node_value = self.NODE_VALUE_TYPE(title)
		return node_value

class CreateTree_MainGroup(CreateTree):
	NODE_VALUE_TYPE = MainGroup

	def _get_all_titles(self) -> list[Title]:
		return get_all_main_group(self.df)

	def _filter_by_title(self, title: Title) -> DataFrame:
		return self.df[ filter_main_group(self.df, title) ]

	def _create_sub_tree(self, filtered_df: DataFrame, path: NodePath) -> Tree:
		return CreateTree_SubGroup(filtered_df, path)()
