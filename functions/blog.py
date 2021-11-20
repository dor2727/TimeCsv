#!/usr/bin/env python3
from TimeCsv import DataFolder, \
					ExtraDetailsFilter, GroupFilter, \
					DetailedStats_ExtraDetails


# requires `self._extra_details_name`
class DetailedStats_Blog(DetailedStats_ExtraDetails):
	_extra_details_name = None
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._filter_obj = (
			ExtraDetailsFilter(self._extra_details_name)
			 &
			GroupFilter("Blog")
		)

		self._initialize_data()

class DetailedStats_Blog_Sketch(DetailedStats_Blog):
	_extra_details_name = "sketch"
class DetailedStats_Blog_Research(DetailedStats_Blog):
	_extra_details_name = "research"
class DetailedStats_Blog_Manim(DetailedStats_Blog):
	_extra_details_name = "manim"

def get_blog_statistics(datafolder=None):
	datafolder = datafolder or DataFolder()
	data = datafolder.data

	statistics = [
		DetailedStats_Blog_Sketch  (data, grouping_method="time"),
		DetailedStats_Blog_Research(data, grouping_method="time"),
		DetailedStats_Blog_Manim   (data, grouping_method="time"),
	]

	for s in statistics:
		print("==============")
		print(s._extra_details_name)
		print("==============")
		print(s.to_text())
		s.to_pie(save=False)
		print()

if __name__ == '__main__':
	get_blog_statistics()
