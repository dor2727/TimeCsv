from typing import Literal

from .title_types import *

NodeType = (
	  int # 0 for main group, 1/2/3 for len(groups)==2/3/4
	| Literal["description"]
	| Literal["extra_details"] | Literal["extra_details_keys"]
	| Literal["extra_details_values"]
)

def get_representative_nodes(nodes: list[Node], requested_type: NodeType) -> list[Node]:
	if isinstance(requested_type, str) and requested_type.isdigit():
		requested_type = int(requested_type)

	if isinstance(requested_type, int):
		if requested_type == 0:
			return _get_representative_nodes_main_group(nodes)
		else:
			return _get_representative_nodes_sub_group(nodes, requested_type)
	else:
		if requested_type == "description":
			return _get_representative_nodes_description(nodes)
		elif requested_type in ("extra_details", "extra_details_keys"):
			return _get_representative_nodes_extra_details_keys(nodes)
		elif requested_type == "extra_details_values":
			return _get_representative_nodes_extra_details_values(nodes)
	raise ValueError(f"Invalid \"requested_type\" given, Allowed values are: {NodeType}")

def _get_representative_nodes_by_type(nodes: list[Node], last_type: type) -> list[Node]:
	return list(filter(
		lambda node: isinstance(node.path[-1], last_type),
		nodes
	))

def _get_representative_nodes_main_group(nodes: list[Node]) -> list[Node]:
	return _get_representative_nodes_by_type(nodes, MainGroup)

def _get_representative_nodes_sub_group(nodes: list[Node], index: int) -> list[Node]:
	return list(filter(
		lambda node: (
			isinstance(node.path[0], MainGroup)
			 and
			(len(node.path) == index+1)
			 and
			all(isinstance(p, SubGroup) for p in node.path[1: index+1])
		),
		nodes
	))

def _get_representative_nodes_description(nodes: list[Node]) -> list[Node]:
	return _get_representative_nodes_by_type(nodes, Description)

def _get_representative_nodes_extra_details_keys(nodes: list[Node]) -> list[Node]:
	return _get_representative_nodes_by_type(nodes, ExtraDetailsKey)

def _get_representative_nodes_extra_details_values(nodes: list[Node]) -> list[Node]:
	return _get_representative_nodes_by_type(nodes, ExtraDetailsValue)
