from pandas import DataFrame
from argparse import Namespace

from ..tree import create_tree, SORT_FUNCTIONS, flatten_tree, get_representative_nodes
from ..tree.title_types import Tree, Node

from .files import open_data_file
from .cli import parse_args
from .filter_time import filter_df_by_time
from .filter_content import filter_df_by_content
from .output_pie import handle_pie
from .output_terminal import handle_terminal

def get_df(args: Namespace) -> DataFrame:
	data_file = open_data_file(args.file)
	return data_file.to_dataframe()

def get_tree(df: DataFrame, args: Namespace) -> Tree:
	tree = create_tree(df)
	tree = SORT_FUNCTIONS[args.sort_method](tree)
	return tree

def get_nodes(tree: Tree, args: Namespace) -> list[Node]:
	nodes = flatten_tree(tree)
	edge_nodes = get_representative_nodes(nodes, args.max_hirarchy)
	return edge_nodes

def main():
	args = parse_args()

	root_df = get_df(args)
	root_df = filter_df_by_time(root_df, args)
	root_df = filter_df_by_content(root_df, args)

	tree = get_tree(root_df, args)
	edge_nodes = get_nodes(tree, args)

	if args.pie:
		return handle_pie(root_df, tree, edge_nodes, args)
	else:
		return handle_terminal(root_df, tree, edge_nodes, args)
