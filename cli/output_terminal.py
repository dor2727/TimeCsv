from pandas import DataFrame
from argparse import Namespace

from ..tree.title_types import Tree, Node
from ..plotting.terminal import format_all_paths_for_nodes, print_nodes, print_summary_line


def handle_terminal(root_df: DataFrame, tree: Tree, edge_nodes: list[Node], args: Namespace):
	formatted_paths = format_all_paths_for_nodes(edge_nodes)
	total_root_seconds = root_df.total_seconds.sum()

	try:
		print_nodes(formatted_paths, edge_nodes, total_root_seconds)
		print_summary_line(root_df)
	except BrokenPipeError:
		# probably we are called as `python ... | head`
		pass
