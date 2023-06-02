from pandas import DataFrame

from .tree import create_tree, flatten_tree, get_representative_nodes, NodeType
from .statistics import DFStats
from .plotting.terminal import format_all_paths_for_nodes
from .parsing import DataFile

def main(root_df: DataFrame, requested_type: NodeType=0):
	tree = create_tree(root_df)
	nodes = flatten_tree(tree)
	edge_nodes = get_representative_nodes(nodes, requested_type)

	formatted_paths = format_all_paths_for_nodes(edge_nodes)

	for formatted_path, node in zip(formatted_paths, edge_nodes):
		print(formatted_path, '-', DFStats(node.filtered_df).stats())

if __name__ == '__main__':
	df = DataFile("data/Work/2023_classiq_20_percent.tcsv").to_dataframe()
	# main(df, "description")
	main(df, 1)
