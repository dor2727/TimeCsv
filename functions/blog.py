import TimeCsv.statistics
from TimeCsv.parsing import DataFolder
from TimeCsv.filters import *

class ExtraDetailsBlogStats(TimeCsv.statistics.GroupedStats):
	_extra_details_name = "sketch"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._filter_obj = (
			GroupFilter("Blog")
			 &
			DescriptionFilter(self._extra_details_name)
		)

		self._initialize_data()

	def _initialize_data(self):
		self._original_data = self.data
		self.data = self._filter_obj % self.data

	def _get_extra_details(self, obj):
		if not hasattr(obj, "extra_details"):
			return "<no extra details>"
		if not obj.extra_details:
			return "<no extra details>"
		e = obj.extra_details.get(self._extra_details_name, "<no extra details>")
		return e.split(EXTRA_DETAILS_SEPERATOR)[0]

	def _get_headers(self):
		# get all headers
		headers = set()

		for i in self.data:
			headers.add(self._get_extra_details(i))

		# return a list, sorted alphabetically
		self._headers = sorted(headers)
		return self._headers

	def _get_filtered_data_per_header(self, header):
		return list(filter(
			lambda i: self._get_extra_details(i) == header,
			self.data
		))

class ExtraDetailsBlogStats_sketch(ExtraDetailsBlogStats):
	_extra_details_name = "sketch"
class ExtraDetailsBlogStats_research(ExtraDetailsBlogStats):
	_extra_details_name = "research"
class ExtraDetailsBlogStats_manim(ExtraDetailsBlogStats):
	_extra_details_name = "manim"

def get_blog_statistics(datafolder=None):
	datafolder = datafolder or DataFolder()
	d = datafolder.data

	s = [
		ExtraDetailsBlogStats_sketch(d, group_value="time"),
		ExtraDetailsBlogStats_research(d, group_value="time"),
		ExtraDetailsBlogStats_manim(d, group_value="time"),
	]
	for g in s:
		print("==============")
		print("sketch")
		print("==============")
		print(g.group())
		print(g.to_pie(save=False))
		print("==============")
		# pdb to pause python and allow matplotlib to display the image
		import pdb; pdb.set_trace()
