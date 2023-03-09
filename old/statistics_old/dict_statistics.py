from functools import partial

from TimeCsv.statistics.base_statistics import DetailedStats
from TimeCsv.statistics.group_statistics import DetailedStats_Group
from TimeCsv.statistics.extra_info_statistics import DetailedStats_AllGroups
from TimeCsv.statistics.description_statistics import DetailedStats_Description
from TimeCsv.filters.filter_utils import join_filters_with_or
from TimeCsv.filters.base_filters import TrueFilter, Filter
from TimeCsv.utils import re_exact

TITLE_OTHER = "<Other>"
SPECIAL_KEYS = ["_filter", "_group_by"]

STATS_ORDER = [
	# The root filter is showing data by groups
	DetailedStats_AllGroups,
	# Then, grouping each group by its items
	DetailedStats_Group,
	# Then, grouping each description by its extra-details
	DetailedStats_Description,
]



def dict_to_filter(d, root=False):
	# Recursion stop
	if isinstance(d, Filter):
		return d

	# Copy the dict in order to remove SPECIAL_KEYS
	d = d.copy()

	# get the root filter
	root_filter = d.pop("_filter", None)

	# remove special keys
	for i in SPECIAL_KEYS:
		d.pop(i, None)

	# If the root filter is all that's needed, then we're done here
	if root and root_filter:
		return root_filter
	# If there's nothing else, then we're done here
	if root_filter and not d:
		return root_filter

	# Recursion
	f = join_filters_with_or(map(
		partial(dict_to_filter, root=root),
		d.values()
	))

	if root_filter:
		f = root_filter & f

	return f

class DetailedStats_DictOfFilters(DetailedStats):
	def __init__(self, dict_of_filters, name, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._process_dict_of_filters(dict_of_filters)
		self._name = name

	def _process_dict_of_filters(self, dict_of_filters):
		self._raw_dict_of_filters = dict_of_filters

		self._root_filter = self._raw_dict_of_filters.get("_filter", TrueFilter())
		self._group_children_by = self._raw_dict_of_filters.get("_group_by", DetailedStats_AllGroups)

		self._filters = {
			k:v for k,v in self._raw_dict_of_filters.items()
			if k not in SPECIAL_KEYS
		}

	def __repr__(self):
		return f"{self.__class__.__name__}({self._name})"

	# titles
	def _get_titles(self):
		# return a list, sorted alphabetically
		titles = list(self._filters.keys())
		titles += [TITLE_OTHER]
		print(titles)

		self._titles = sorted(titles)
		return self._titles

	# filters
	def _create_other_filter(self):
		if self._filters:
			all_filters = join_filters_with_or(
				dict_to_filter(v, root=True)
				for v in self._filters.values()
			)
			return ~all_filters
		else:
			return TrueFilter()

	def _create_other_filter_old(self):
		all_filters = join_filters_with_or(
			dict_to_filter(v, root=True)
			for k, v in self._dict_of_filters.items()
			if k not in SPECIAL_KEYS
		) or TrueFilter()
		return ~all_filters

	def _get_filter_of_title(self, title):
		if title == TITLE_OTHER:
			return self._create_other_filter()
		else:
			return dict_to_filter(self._filters[title])

	# pie
	def _plot_make_pie_clickable(self, fig, patches):
		def onclick(event):
			# Get the patch and its label
			patch = event.artist
			label = patch.get_label()

			# Create a grouped-stats object for that label
			if label == TITLE_OTHER:
				if "_group_by" in self._dict_of_filters:
					g_cls = self._dict_of_filters["_group_by"]
					if g_cls == DetailedStats_Group:
						g = DetailedStats_Group(
							self._get_items_of_title(label),
							group_name=re_exact(self._name),
							time_filter=self._time_filter,
							grouping_method=self._grouping_method,
							sorting_method=self._sorting_method,
							case_sensitive=False, regex=True,
						)
					elif g_cls == DetailedStats_AllGroups:
						g = DetailedStats_AllGroups(
							self._get_items_of_title(label),
							time_filter=self._time_filter,
							grouping_method=self._grouping_method,
							sorting_method=self._sorting_method,
						)
					else:
						import ipdb; ipdb.set_trace()
				else:
					import ipdb; ipdb.set_trace()
			else:
				# If there's no specific keys, but only a root filter
				if all(i in SPECIAL_KEYS for i in self._dict_of_filters[label]):
					if "_filter" in self._dict_of_filters[label]:
						root_filter = self._dict_of_filters[label]["_filter"]
						if isinstance(root_filter, GroupFilter):
							g = DetailedStats_Group(
								self._get_items_of_title(label),
								group_name=root_filter.string_to_find,
								time_filter=self._time_filter,
								grouping_method=self._grouping_method,
								sorting_method=self._sorting_method,
								case_sensitive=root_filter.case_sensitive, regex=root_filter.regex,
							)
					else:
						import ipdb; ipdb.set_trace()
				else:
					g = DetailedStats_DictOfFilters(
						self._dict_of_filters[label],
						label,
						self._get_items_of_title(label),
						time_filter=self._time_filter,
						grouping_method=self._grouping_method,
						sorting_method=self._sorting_method,
					)

			# Set title prefix
			g._title_prefix = getattr(self, "_title_prefix", '') + f"{self.__class__.__name__}({self._grouping_method}) / "


			print(f"=== {label} ===")
			print(g.to_text())
			g.to_pie(save=False)

		for patch in patches:
			patch.set_picker(True)

		fig.canvas.mpl_connect('pick_event', onclick)
