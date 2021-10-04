#!/usr/bin/rlwrap python3
from TimeCsv.cli.parse_args import parse_args
from TimeCsv.cli.data import get_special_text, get_extra_details_text, get_search_filter_text, \
							 open_data_file, get_data
from TimeCsv.functions.productivity import get_productivity_pie

def main(data_object=None, args_list=None):
	args = parse_args(args_list=args_list)

	data_object = open_data_file(data_object, args.file)

	data, selected_time, search_filter = get_data(data_object, args)

	if args.productive_pie:
		return get_productivity_pie(data, selected_time, save=False, focused=args.productive_pie_focused)
	elif search_filter is None:
		return get_special_text(data, selected_time, args)
	elif search_filter is not None and args.extra_details:
		return get_extra_details_text(data, selected_time, search_filter, args)
	else:
		return get_search_filter_text(data, selected_time, search_filter, args)
