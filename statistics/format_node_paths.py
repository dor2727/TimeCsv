from pandas import DataFrame

from .title_types import *


def format_all_paths_for_nodes(nodes: list[Node], pad: bool=True) -> list[str]:
	paths = [n.path for n in nodes]
	formatted_paths = format_all_paths(paths)
	if pad:
		return pad_paths(formatted_paths)
	else:
		return join_paths(formatted_paths)

def pad_paths(paths: list[list[str]]) -> list[str]:
	max_line_length = get_max_line_length(paths)
	line_format = f"%-{max_line_length}s"

	return [
		'\n'.join(
			line_format % line
			for line in p
		)
		for p in paths
	]

def join_paths(paths: list[list[str]]) -> list[str]:
	return ['\n'.join(p) for p in formatted_paths]

def get_max_line_length(formatted_paths: list[list[str]]):
	return max(
		len(line)
		for s in formatted_paths
		for line in s
	)

def format_all_paths(paths: list[NodePath]) -> list[list[str]]:
	formatted_paths = [format_first_path(paths[0])]

	for prev_path, path in zip(paths[:-1], paths[1:]):
		last_common_index = _get_last_common_path_element(prev_path, path)
		formatted_paths.append(format_path(path, last_common_index))

	return formatted_paths


def format_path(path: NodePath, last_common_index: int) -> list[list[str]]:
	res = []
	for index, title in enumerate(path):
		if index <= last_common_index:
			continue
		res.append(
			pad_start(index, last_common_index)
			 +
			PIPE_GROUPS.split
			 +
			title.colorize()
		)
	return res

def format_first_path(path: NodePath) -> list[list[str]]:
	res = []
	for index, title in enumerate(path):
		res.append(pad_start(index, index) + PIPE_GROUPS.first + title.colorize())
	return res

def _get_last_common_path_element(path1: NodePath, path2: NodePath) -> int:
	last_common_index = -1

	for index, (p1, p2) in enumerate(zip(path1, path2)):
		if p1 == p2:
			last_common_index = index

	return last_common_index

class PIPES:
	root_start = '┌' # ord(9484 )
	add_more = '├' # ord(9500 )
	last = '└' # ord(9492 )
	dash = '─' # ord(9472 )
	continue_ = '│' # ord(9474 )
	space = ' '

class PIPE_GROUPS:
	first = PIPES.root_start + PIPES.dash*2 + PIPES.space
	split = PIPES.add_more   + PIPES.dash*2 + PIPES.space
	last  = PIPES.last       + PIPES.dash*2 + PIPES.space

def pad_start(hirarchy_level: int, last_common_index: int) -> str:
	if hirarchy_level == 0:
		return ''
	else:
		res = ''
		for i in range(hirarchy_level):
			if i <= last_common_index:
				res += PIPES.continue_
			else:
				res += PIPES.space
			res += PIPES.space * 3
		return res
