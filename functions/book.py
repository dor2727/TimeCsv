import re
from pandas import DataFrame

from ..tree.title_types import Tree, Node
from ..filters import (
	join_filters_with_and,
	filter_sub_groups, filter_num_groups,
	filter_description_exact,
	filter_has_extra_details_value_exact, filter_has_extra_details, filter_has_extra_details_key
)
from ..grouping import get_all_description
from ..utils import Seconds, seconds_to_time_str

def main(root_df: DataFrame, tree: Tree, edge_nodes: list[Node]):
	df = filter_only_books(root_df)
	all_books = get_all_description(df)
	for book in all_books:
		print_book_statistics(df, book, max_book_name_length=max(map(len, all_books)))


def filter_only_books(df: DataFrame):
	joined_filters = join_filters_with_and(
		filter_sub_groups(df, "Read", "Book"),
		~ filter_num_groups(df, 2),
		~ filter_sub_groups(df, "Read", "Book", "Audiobook"),
	)
	return df[joined_filters]

def print_book_statistics(df: DataFrame, book: str, max_book_name_length: int):
	filtered_df = df[filter_description_exact(df, book)]

	neto_time: Seconds = sum(filtered_df.total_seconds)
	bruto_time = max(filtered_df.stop_time) - min(filtered_df.start_time)
	amount_of_pages, time_per_page = calculate_time_per_page(filtered_df, book, neto_time)

	s = f"{book:<{max_book_name_length}s} : read time neto = {seconds_to_time_str(neto_time)} : read time bruto = {bruto_time}"
	if time_per_page is not None:
		s += f" : time per page = {time_per_page:.0f} sec ({amount_of_pages} pages)"
	print(s)

def calculate_time_per_page(filtered_df: DataFrame, book: str, reading_time: Seconds):
	df_1 = filtered_df[filter_has_extra_details(filtered_df)]
	df_2 = df_1[filter_has_extra_details_key(df_1, book)]
	single_item_df = df_2[filter_has_extra_details_value_exact(df_2, book, "done")]

	if single_item_df.empty:
		return None, None

	extra_details_values = single_item_df.extra_details.str[book]
	last_page_number = extract_page_number(extra_details_values)
	if last_page_number is None:
		return None, None

	time_per_page = reading_time / last_page_number
	return last_page_number, time_per_page

page_pattern = re.compile("at page (\\d+)")

def extract_page_number(extra_details_values: list[str]):
	for s in extra_details_values.item():
		if pages := page_pattern.findall(s):
			return int(pages[0])
	return None
