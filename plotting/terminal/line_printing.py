from pandas import DataFrame

from ...tree.title_types import Node
from ...statistics import NoParentDFStats
from .format_node_paths import PIPES

def print_single_line(formatted_path: str, node: Node, total_root_seconds: int):
	print(formatted_path, '-', node.stats.stats(total_root_seconds))

def print_nodes(formatted_paths: list[str], nodes: list[Node], total_root_seconds: int):
	for formatted_path, node in zip(formatted_paths, nodes):
		print_single_line(formatted_path, node, total_root_seconds)

def print_summary_line(root_df: DataFrame):
	print(PIPES.dash * 50)
	print(f"Total - {NoParentDFStats(root_df).stats_short()}")
