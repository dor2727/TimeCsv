from pandas import DataFrame
from numpy import ndarray
from functools import reduce


def get_unique_values(df: DataFrame, attr_name: str) -> ndarray:
	return getattr(df, attr_name).unique()
def get_unique_values_at_index(df: DataFrame, attr_name: str, index: int) -> ndarray:
	return getattr(df, attr_name).str[index].unique()

def union_of_df_of_iterables(df: DataFrame) -> set:
	return reduce(
		set.union,
		map(
			set,
			df.values
		)
	)
