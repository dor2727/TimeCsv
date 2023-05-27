from pandas import DataFrame

from .base_plotter import BasePlotter, FilteredDF
from .consts import SortingMethods

def sort_alphabetically(filtered_dfs: list[DataFrame]):
	return sorted(
		filtered_dfs,
		key=lambda fdf: fdf.group_name,
	)
def sort_by_total_time(filtered_dfs: list[DataFrame]):
	return sorted(
		filtered_dfs,
		key=lambda fdf: fdf.statistics.total_seconds,
		reverse=True
	)
def sort_by_num_events(filtered_dfs: list[DataFrame]):
	return sorted(
		filtered_dfs,
		key=lambda fdf: fdf.statistics.num_events,
		reverse=True
	)

sort_function = {
	SortingMethods.Alphabetically : sort_alphabetically,
	SortingMethods.TotalTime : sort_by_total_time,
	SortingMethods.NumEvents : sort_by_num_events,
}

class TerminalBasicPlotter(BasePlotter):
	def _generate_titles(self, filtered_df: list[FilteredDF]):
		# TODO
		# import ipdb; ipdb.set_trace()
		for f_df in filtered_df:
			yield f_df, f_df.group_name

	def print_single_line(self, filtered_df: FilteredDF, pretty_group_name: str) -> str:
		print(f"%-{self.max_group_name_length}s (%4d) : %s" % (
				pretty_group_name,
				filtered_df.statistics.num_events,
				filtered_df.statistics.total_seconds_str
			))

	def print_header(self):
		print("%s -> %s (%4d events)" % (
			self.df.date.min().date(),
			self.df.date.max().date(),
			self.df.shape[0],
		))

	@property
	def sort_function(self):
		return sort_function[self.sorting_method]

	def basic_plot(self):
		self.print_header()

		sorted_filtered_df = self.sort_function(self.filtered_dfs)
		filtered_df_and_titles = self._generate_titles(sorted_filtered_df)
		for filtered_df, pretty_group_name in filtered_df_and_titles:
			self.print_single_line(filtered_df, pretty_group_name)
