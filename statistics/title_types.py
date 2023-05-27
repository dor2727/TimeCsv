from datetime import datetime
from collections import namedtuple

class MainGroup(str): pass
class SubGroup(str): pass
class NoneSubGroup(SubGroup):
	# avoinding hash-collision on empty strings
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._creation_time = datetime.now()
	def __hash__(self):
		return hash(self._creation_time)
class Description(str): pass
class ExtraDetailsKey(str): pass
class ExtraDetailsValue(str): pass
Hirarchy = MainGroup | SubGroup | NoneSubGroup | Description | ExtraDetailsKey | ExtraDetailsValue

NodePath = tuple[Hirarchy, ...]
Node = namedtuple("Node", [
	"path",        # NodePath
	"filtered_df", # DataFrame
	"sub_trees",   # Tree
])
Tree = dict[Hirarchy, Node]
