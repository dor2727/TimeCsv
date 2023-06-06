from datetime import datetime
from collections import namedtuple

class Title:
	def __init__(self, s: str):
		self.s = s

	def __str__(self):
		return self.s
	def __len__(self):
		return len(self.s)
	def __hash__(self):
		return str.__hash__(self.s)
	def __eq__(self, other):
		if isinstance(other, str):
			return self.s == other
		else:
			return super().__eq__(other)

	def __repr__(self):
		return f"{self.__class__.__name__}({self.s})"

class MainGroup(Title): pass
class SubGroup(Title): pass
class NoneSubGroup(SubGroup):
	# avoinding hash-collision on empty strings
	def __init__(self, *args, **kwargs):
		super().__init__("__Main__", *args, **kwargs)
		self._creation_time = datetime.now()
	def __hash__(self):
		return hash(self._creation_time)

class Description(Title): pass
class ExtraDetailsKey(Title): pass
class ExtraDetailsValue(Title): pass

NodePath = tuple[Title, ...]
Node = namedtuple("Node", [
	"path",        # NodePath
	"filtered_df", # DataFrame
	"stats",       # DFStats
	"sub_trees",   # Tree
])
Tree = dict[Title, Node]
