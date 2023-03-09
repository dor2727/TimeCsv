import sys
import argparse

from ..utils.consts import DEFAULT_DATA_DIRECTORY


# may pass arguments as a list (used in the telegram bot)
def parse_args(args_list=None):
	parser = argparse.ArgumentParser()
	parser.add_argument("--file", "--folder", "-f", type=str, default=DEFAULT_DATA_DIRECTORY, dest="file", help="which file/folder to read")


	if args_list is None:
		args = parser.parse_args()
	else:
		args = parser.parse_args(args_list)

	return args
