from .cli import parse_args, open_data_file

from TimeCsv import *


def main():
	args = parse_args()

	df = open_data_file(args.file).to_dataframe()

	bp = TerminalBasicPlotter(
		df,
		get_all_main_group,
		filter_main_group
	)
	bp.basic_plot()

if __name__ == '__main__':
	main()
