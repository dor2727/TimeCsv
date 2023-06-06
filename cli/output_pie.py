from pandas import DataFrame
from argparse import Namespace

from ..tree.title_types import Tree, Node


def handle_pie(root_df: DataFrame, tree: Tree, edge_nodes: list[Node], args: Namespace):
	# if args is some specific search:
	# call get_nodes, and pie them
	# else:
	# pie the root tree
	pass