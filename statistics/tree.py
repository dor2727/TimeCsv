from pandas import DataFrame
import numpy as np
from datetime import datetime

from ..filters import *
from ..grouping import *

class MainGroup(str): pass
class SubGroup(str): pass
class NoneSubGroup(SubGroup):
	# avoinding hash-collision on empty strings
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._creation_time = datetime.now()
	def __hash__(self):
		return hash(self._creation_time)
class Description(str): pass
class ExtraDetailsKey(str): pass
class ExtraDetailsValue(str): pass
Hirarchy = MainGroup | SubGroup | NoneSubGroup | Description | ExtraDetailsKey | ExtraDetailsValue

NodePath = tuple[Hirarchy, ...]

NodeValues = tuple[Hirarchy, DataFrame, "Tree"]
Tree = dict[Hirarchy, NodeValues]

def df_to_tree(df: DataFrame):
	# root level: MainGroup
	pass
	
def _create_tree_at_level_main_group(df: DataFrame) -> Tree:
	tree = {}

	for main_group in get_all_main_group(df):
		node_value = MainGroup(main_group)
		node_path = (node_value,)
		filtered_df = df[filter_main_group(df, main_group)]
		sub_trees = _create_tree_at_level_sub_group(filtered_df, node_path)
		tree[node_value] = (node_path, filtered_df, sub_trees)

	return tree

def _create_tree_at_level_sub_group(df: DataFrame, current_path: NodePath, sub_group_level: int=1) -> Tree:
	all_sub_groups = get_all_sub_groups_at_index(df, sub_group_level)

	if len(all_sub_groups) == 1 and isinstance(all_sub_groups[0], float) and np.isnan(all_sub_groups[0]):
		tree = _create_tree_at_level_description(df, current_path)
	else:
		tree = {}

		for sub_group in all_sub_groups:
			if isinstance(sub_group, float) and np.isnan(sub_group):
				node_value = NoneSubGroup()
			else:
				node_value = SubGroup(sub_group)
			node_path = current_path + (node_value,)
			filtered_df = df[filter_group_at_index(df, sub_group, sub_group_level)]
			sub_trees = _create_tree_at_level_sub_group(filtered_df, node_path, sub_group_level+1)
			tree[node_value] = (node_path, filtered_df, sub_trees)

	return tree

def _create_tree_at_level_description(df: DataFrame, current_path: NodePath) -> Tree:
	tree = {}

	for description in get_all_description(df):
		node_value = Description(description)
		node_path = current_path + (node_value,)
		filtered_df = df[filter_description_exact(df, description)]
		sub_trees = _create_tree_at_level_extra_details(filtered_df, node_path)
		tree[node_value] = (node_path, filtered_df, sub_trees)

	return tree

def _create_tree_at_level_extra_details(df: DataFrame, current_path: NodePath) -> Tree:
	tree = {}

	for extra_details_key in get_all_extra_details_keys(df):
		node_value = ExtraDetailsKey(extra_details_key)
		node_path = current_path + (node_value,)
		filtered_df = df[filter_has_extra_details_key(df, extra_details_key)]
		sub_trees = _create_tree_at_level_extra_details_value(filtered_df, node_path, extra_details_key)
		tree[node_value] = (node_path, filtered_df, sub_trees)

	return tree

def _create_tree_at_level_extra_details_value(df: DataFrame, current_path: NodePath, extra_details_key: str) -> Tree:
	tree = {}

	for extra_details_value in get_all_extra_details_values(df, extra_details_key):
		node_value = ExtraDetailsValue(extra_details_value)
		node_path = current_path + (node_value,)
		filtered_df = df[filter_has_extra_details_value_exact(df, extra_details_key, extra_details_value)]
		sub_trees = {}
		tree[node_value] = (node_path, filtered_df, sub_trees)

	return tree
