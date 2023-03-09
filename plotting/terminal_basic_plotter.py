from pandas import DataFrame

from .base_plotter import BasePlotter
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
	def print_single_line(self, filtered_df) -> str:
		print(f"%-{self.max_group_name_length}s (%4d) : %s" % (
				filtered_df.group_name,
				filtered_df.statistics.num_events,
				filtered_df.statistics.total_seconds_str
			))

	def print_header(self):
		print("%s -> %s (%4d events)" % (
			self.df.date.min(),
			self.df.date.max(),
			self.df.shape[0],
		))

	def basic_plot(self):
		self.print_header()

		for filtered_df in sort_function[self.sorting_method](self.filtered_dfs):
			self.print_single_line(filtered_df)
