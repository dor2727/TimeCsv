import argparse
from pandas import DataFrame

from ..filters import join_filters_with_or, join_filters_with_and, filter_content_auto


def filter_df_by_content(df: DataFrame, args: argparse.Namespace):
	if not args.search_string:
		return df

	if args.search_use_or:
		combine = join_filters_with_or
	else:
		combine = join_filters_with_and

	joined_filters = combine(
		filter_content_auto(df, search_string)
		for search_string in args.search_string
	)

	return df[joined_filters]
