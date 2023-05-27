from dataclasses import dataclass
# from .color import COLORS, single_color

@dataclass
class Node:
	name: str
	color: str

	children: list["Node"]
	max_child_length: int

EMPTY_NODE = Node('', '', [], 0)
EMPTY_NODE_TUPLE = (EMPTY_NODE,)

def dict_to_tree(d: dict, recurse_level: int=0) -> Node:
	root_nodes = []

	for k, v in d.items():
		if isinstance(v, dict):
			v_nodes = dict_to_tree(v, recurse_level+1).children
		else:
			v_nodes = [
				Node(str(v), COLORS[4], [], 0)
			]

		root_nodes.append(
			Node(
				k,
				COLORS[recurse_level+1],
				v_nodes,
				# max(len(n.name) for n in v_nodes) + 1 + max(n.max_child_length for n in v_nodes)
				max(len(n.name) for n in v_nodes)
			)
		)

	return Node(
		"__root__",
		'',
		root_nodes,
		max(len(n.name) for n in root_nodes)
	)

def format_hirarchically(nodes: list[Node]) -> list[tuple[Node]]:
	lines = []

	for node in nodes:
		if node.children:
			for formatted_child in format_hirarchically(node.children):
				lines.append( (node,) + formatted_child )
		else:
			lines.append( (node,) )

	max_line_length = max(map(len, lines))
	prepended_lines = []
	for line in lines:
		length_diff = max_line_length - len(line)
		prepended_lines.append( EMPTY_NODE_TUPLE*length_diff + line )
	return prepended_lines

CONNECTOR = COLORIZE[0]('-')

def format_lines(lines: list[tuple[Node]]):
	levels = max(map(len, lines))
	lengths = [get_length_of_level(lines, i) for i in range(levels)]
	formatted_lines = []

	for line in lines:
		formatted_lines.append(
			CONNECTOR.join(
				f"%-{lengths[i]}s" % single_color(line[i].name, line[i].color)
				for i in range(len(line))
			)
		)
	return formatted_lines

def get_length_of_level(lines: list[tuple[Node]], level_index: int) -> int:
	return max(
		map(
			lambda line: len(line[level_index].name),
			filter(
				lambda line: len(line) > level_index,
				lines
			)
		)
	)


from pprint import pprint
example = {
	"root_1": {
		"sub_1": 1,
		"sub_2": 2,
	},
	"roooooot_2": 3,
	"root_3": {
		"sub_1": 4,
		"sub_2": {
			"child_1": 5,
			"child_2": 6,
		},
	},
}

example_nodes = dict_to_tree(example).children
example_lines = format_hirarchically(example_nodes)
pretty_lines = format_lines(example_lines)
