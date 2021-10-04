
class ExtraDetailsGroupedStats(GroupedStats):
	# _allowed_group_values = ("time", "amount", "total_amount")
	"""
	requires:
		self._filter_obj
		self._extra_details_name

		and requires a call to self._initialize_data in __init__
			since it requires self._filter_obj
	"""
	def _initialize_data(self):
		self._original_data = self.data
		self.data = self._filter_obj % self.data

	def _get_headers(self):
		# get all headers
		headers = set()

		for i in self.data:
			h = i.extra_details[self._extra_details_name]
			if h:
				headers.update(h)

		# return a list, sorted alphabetically
		self._headers = sorted(headers)
		return self._headers

	def _get_filtered_data_per_header(self, header):
		return list(filter(
			lambda i: header in i.extra_details[self._extra_details_name],
			self.data
		))

class GroupedStats_ExtraDetailGeneric(ExtraDetailsGroupedStats):
	def __init__(self, search_filter, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._filter_obj = (
			search_filter
			 &
			HasExtraDetailsFilter()
			 &
			~DescriptionFilter('&') # TODO: remove me. This is a patch since '&' is not parsed yet
		)

		self._initialize_data()

		self._get_extra_details_name()

	def _get_extra_details_name(self):
		names = sum(
			(list(i.extra_details.keys()) for i in self.data),
			[]
		)
		names = list(set(names))

		if len(names) == 1:
			self._extra_details_name = names[0]
		elif len(names) == 0:
			raise ValueError("No possible extra_details_name found")
		else:
			# TODO: maybe use the most frequent name?
			print(names)
			raise ValueError(f"Too many ({len(names)}) possible extra_details_name found")

		return self._extra_details_name

class GroupedStats_Lecture(ExtraDetailsGroupedStats):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._extra_details_name = "lecture"

		self._filter_obj = (
			DescriptionFilter("lecture ")
			 &
			HasExtraDetailsFilter()
			 &
			~GroupFilter("University")
		)

		self._initialize_data()

class GroupedStats_Homework(ExtraDetailsGroupedStats):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._extra_details_name = "homework"

		self._filter_obj = (
			DescriptionFilter("homework")
			 &
			HasExtraDetailsFilter()
			 &
			GroupFilter("University")
		)

		self._initialize_data()

class GroupedStats_Shower(ExtraDetailsGroupedStats):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._extra_details_name = "shower"

		self._filter_obj = (
			DescriptionFilter("shower")
			 &
			HasExtraDetailsFilter()
		)

		self._initialize_data()

class GroupedStats_PrepareFood(ExtraDetailsGroupedStats):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._extra_details_name = "prepare"

		self._filter_obj = (
			DescriptionFilter("prepare")
			 &
			GroupFilter("Food")
			 &
			HasExtraDetailsFilter()
		)

		self._initialize_data()

