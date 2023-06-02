import os
import sys
import logging
import datetime

from .consts import *
from TimeCsv.utils import get_midnight


#
# getting the key
#
def read_file(filename):
	handle = open(filename)
	data = handle.read().strip()
	handle.close()
	return data


def get_folder_files(folder, recursive=False):
	w = os.walk(folder)

	if recursive:
		all_files = []
		for folder_name, folders, files in w:
			all_files += list(map(
				lambda file_name: os.path.join(folder_name, file_name),
				files
			))
		return all_files

	else:
		folder_name, folders, files = next(w)
		return list(map(
			lambda file_name: os.path.join(folder_name, file_name),
			files
		))


#
# Logging
#
def initialize_logger(debug=False):
	logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")

	rootLogger = logging.getLogger()
	if debug:
		rootLogger.setLevel(logging.DEBUG)
	else:
		rootLogger.setLevel(logging.INFO)

	fileHandler = logging.FileHandler(LOG_FILE_PATH)
	fileHandler.setFormatter(logFormatter)
	rootLogger.addHandler(fileHandler)

	consoleHandler = logging.StreamHandler(sys.stdout)
	consoleHandler.setFormatter(logFormatter)
	rootLogger.addHandler(consoleHandler)

	rootLogger.info("---------------------------------------")



"""
A small util, getting the 'message' object from telegram's 'update' object
"""
def get_message(update):
	if update["message"] is not None:
		return update["message"]
	else:
		return update["callback_query"]["message"]
"""
"""
def get_chat_id(update):
	return get_message(update)['chat']['id']

	# another way
	# return context._chat_id_and_data[0]
	# return context._user_id_and_data[0]


#
# Handling functions' names
#
def strip_command_name(command_name):
	return command_name[8:]
def is_command_name(command_name):
	return command_name.startswith("command_")

def generate_menu_patter(menu_name):
	return f"^{menu_name}\\b"
def is_menu_name(menu_name):
	return menu_name.startswith("menu_")

def is_chat_id(file_name):
	return os.path.basename(file_name).startswith("chat_id_")
def get_chat_id_username(file_name):
	user_name = os.path.basename(file_name)[8:]
	if not user_name:
		user_name = "<no_name>"
	return user_name
def get_chat_id_from_file_name(file_name):
	return int(read_file(file_name))

#
# Time Utils
#
from TimeCsv import TimeFilter_Days     , \
					TimeFilter_DateRange, \
					TimeFilter_Month    , \
					TimeFilter_Year
from TimeCsv.filters.base_filters import TrueFilter
from TimeCsv.utils import get_midnight
from TimeCsv.consts import WEEK_STARTS_AT_SUNDAY
def get_named_filter(name, args=None):
	if name == "today":
		if args is None:
			return TimeFilter_Days(1)
		elif type(args) is int:
			return TimeFilter_Days(args)
		else:
			return TimeFilter_Days(*args)

	elif name == "yesterday":
		stop_time  = get_midnight( datetime.datetime.now() )
		start_time = get_midnight(
			stop_time
			 -
			datetime.timedelta(days=1)
		)

		return TimeFilter_DateRange( start_time, stop_time )

	elif name == "week":
		return TimeFilter_Days(7)

	elif name == "last_week":
		today = datetime.datetime.now()

		if WEEK_STARTS_AT_SUNDAY:
			weekday = today.weekday() + WEEK_STARTS_AT_SUNDAY
			if weekday == 7:
				weekday = 0
		else:
			weekday = today.weekday()
		this_sunday = get_midnight(today - datetime.timedelta(days=weekday))
		prev_sunday = this_sunday - datetime.timedelta(days=7)

		return TimeFilter_DateRange( prev_sunday, this_sunday )

	elif name == "month":
		if args is None:
			return TimeFilter_Month()
		elif type(args) is int:
			return TimeFilter_Month(args)
		else:
			return TimeFilter_Month(*args)

	elif name == "year":
		if args is None:
			return TimeFilter_Year()
		elif type(args) is int:
			return TimeFilter_Year(args)
		else:
			return TimeFilter_Year(*args)

	elif name == "all":
		return TrueFilter()

	else:
		return None
