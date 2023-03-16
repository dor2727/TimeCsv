from .plotting.consts import Outputs
from .filters import join_filters_with_or, join_filters_with_and, filter_content_auto
from .cli import parse_args, open_data_file, filter_by_time, filter_by_content

from TimeCsv import *


group_by = {
	"main_group" : (get_all_main_group , filter_main_group       ),
	"description": (get_all_description, filter_description_exact),
	"friends"    : (get_all_friends    , filter_friends_contain  ),
	"location"   : (get_all_locations  , filter_location_exact   ),
	"vehicle"    : (get_all_vehicles   , filter_vehicle_exact    ),
}

def handle_plotter(df, args):
	if args.list_group_by_options:
		print(group_by.keys())
		return

	if args.output == Outputs.Terminal:
		bp = TerminalBasicPlotter(
			df,
			args.sort_by,
			*group_by[args.group_by]
		)
		bp.basic_plot()
	elif args.output == Outputs.Pie:
		print("WIP - pie chart")
	else:
		raise ValueError("Invalid output. Please choose either \"Terminal\" or \"Pie\"")

def main():
	args = parse_args()

	df = open_data_file(args.file).to_dataframe()

	df = filter_by_time(df, args)
	df = filter_by_content(df, args)

	handle_plotter(df, args)

if __name__ == '__main__':
	main()
