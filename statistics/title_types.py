from datetime import datetime
from collections import namedtuple

from .colors import *

class ColorizedStr:
	def __init__(self, s: str):
		self.s = s

	def __str__(self):
		return self.s
	def __len__(self):
		return len(self.s)

	def __repr__(self):
		return f"{self.__class__.__name__}({self.s})"

	def colorize(self):
		return single_color(self.s, self.color)

class MainGroup(ColorizedStr):
	color = H1
class SubGroup(ColorizedStr):
	color = H2
class NoneSubGroup(SubGroup):
	# avoinding hash-collision on empty strings
	def __init__(self, *args, **kwargs):
		super().__init__("__Main__", *args, **kwargs)
		self._creation_time = datetime.now()
	def __hash__(self):
		return hash(self._creation_time)

class Description(ColorizedStr):
	color = H3
class ExtraDetailsKey(ColorizedStr):
	color = H4
class ExtraDetailsValue(ColorizedStr):
	color = H5
Hirarchy = MainGroup | SubGroup | NoneSubGroup | Description | ExtraDetailsKey | ExtraDetailsValue

NodePath = tuple[Hirarchy, ...]
Node = namedtuple("Node", [
	"path",        # NodePath
	"filtered_df", # DataFrame
	"sub_trees",   # Tree
])
Tree = dict[Hirarchy, Node]
