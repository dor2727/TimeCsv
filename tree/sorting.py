from collections import OrderedDict
import enum

from .title_types import *


def sort_tree(t: Tree, sort_func: callable, **sorted_kwargs) -> Tree:
	# an empty t will stop the recursion automatically
	return OrderedDict(
		(title, sort_node(node, sort_func, **sorted_kwargs))
		for title, node in sorted(t.items(), key=sort_func, **sorted_kwargs)
	)

def sort_node(node: Node, sort_func: callable, **sorted_kwargs) -> Node:
	return Node(
		node.path,
		node.filtered_df,
		node.stats,
		sort_tree(node.sub_trees, sort_func, **sorted_kwargs)
	)


def sort_noop(t: Tree) -> Tree:
	return t

def sort_alphabetically(t: Tree) -> Tree:
	return sort_tree(t, _sort_alphabetically)

def _sort_alphabetically(t: tuple[Title, Node]):
	title = t[0]
	if isinstance(title, NoneSubGroup):
		name = ''
	else:
		name = str(title)
	return name

def sort_by_total_time(t: Tree) -> Tree:
	return sort_tree(t, _sort_by_total_time, reverse=True)

def _sort_by_total_time(t: tuple[Title, Node]):
	node = t[1]
	df = node.filtered_df
	total_seconds = df.total_seconds.sum()
	return total_seconds


class SortingMethods(enum.Enum):
	noop = enum.auto()
	alphabetical = enum.auto()
	total_time = enum.auto()

SORT_FUNCTIONS = {
	SortingMethods.noop: sort_noop,
	SortingMethods.alphabetical: sort_alphabetically,
	SortingMethods.total_time: sort_by_total_time,
}
