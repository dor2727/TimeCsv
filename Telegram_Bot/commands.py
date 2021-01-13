#!/usr/bin/env python3
import os
import pdb
import sys
import time
import shlex
import schedule
import threading
import traceback

import TimeCsv.cli
from TimeCsv.parsing import DataFolder, ParseError

from TimeCsv.consts import *
from TimeCsv.filters import *
from TimeCsv.statistics import *
from TimeCsv.time_utils import read_telegram_file, log, wget
from TimeCsv.functions.productivity import get_productivity_pie

from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_message(update):
	if update["message"] is not None:
		return update['message']
	else:
		return update['callback_query']['message']


# wrappers
def log_command(func):
	def func_wrapper(*args, **kwargs):
		# each function is named "command_something"
		command_name = func.__name__[8:]

		if "scheduled" in kwargs:
			if kwargs["scheduled"]:
				log(f"    [*] scheduled command - {command_name}\t{time.asctime()}")
			kwargs.pop("scheduled")
		else:
			# args[1] is update
			if len(args) > 1 and args[1]:
				update = args[1]
				if update["message"] is not None:
					command_text = update['message']['text']
				else:
					command_text = update['callback_query']['data']
			else:
				command_text = "None"
			log(f"    [*] got command - {command_text}\tcalling {command_name}\t{time.asctime()}")

		return func(*args, **kwargs)

	return func_wrapper

def void(*args, **kwargs):
	return None

"""
requires:
	1) self.user_chat_ids - a list of ints
	2) self.user_names    - a list of strings, in the same length as self.user_chat_ids
"""
def whitelisted_command(func):
	def func_wrapper(*args, **kwargs):
		self = args[0]
		if len(args) > 1 and args[1]:
			update = args[1]

			chat_id = get_message(update)['chat']['id']

			if chat_id == self._chat_id:
				log(f"[+] whitelist - success - {chat_id}")
			else:
				log(f"[-] whitelist - error - {chat_id}")
				log(str(update))
				log('\n')
				return void
		else:
			# scheduled command
			log(f"[*] whitelist - ignored (scheduled)")

		return func(*args, **kwargs)

	return func_wrapper


class TelegramServer(object):
	def __init__(self):
		# server initialization
		self._key = read_telegram_file("key")
		self._chat_id = int(read_telegram_file("chat_id"))

		self.updater = Updater(self._key, use_context=True)
		self.dp = self.updater.dispatcher

		# get a handle to DataFolder
		self.datafolder = DataFolder()

	def chat_id(self, update=None):
		if update:
			return get_message(update)['chat']['id']
		else:
			return self._chat_id

	def send_text(self, text, update=None):
		self.updater.bot.sendMessage(
			self.chat_id(update),
			text
		)

	def send_image(self, image_file, update=None):
		self.updater.bot.send_photo(
			self.chat_id(update),
			photo=image_file
		)

	def loop(self):
		log("[*] entering loop")
		self.updater.start_polling()
		self.updater.idle()

class TelegramCommands(object):
	def _command_name(self, c):
		return c[8:]

	def add_all_handlers(self):
		# register commands
		commands = filter(
			lambda s: s.startswith("command_"),
			dir(self)
		)

		for command_name in commands:
			self.dp.add_handler(CommandHandler(
				self._command_name(command_name),
				getattr(self, command_name)
			))

		# register menus
		menus = filter(
			lambda s: s.startswith("menu_"),
			dir(self)
		)

		for menu_name in menus:
			self.dp.add_handler(CallbackQueryHandler(
				getattr(self, menu_name),
				pattern=f"^{menu_name}\\b",
			))

	def parse_args(self, context, *expected_types):
		result = []
		if context and context.args:
			try:
				for i in range(len(context.args)):
					result.append(expected_types[i](context.args[i]))
			except Exception as e:
				self.send_text(
					f"command_month error: {e} ; args = {context.args}",
					# send it to me, not to the user (avoiding information disclosure)
					self.chat_id()
				)

		# fill default values, if needed
		for i in range(len(result), len(expected_types)):
			result.append(expected_types[i]())

		return result


	@whitelisted_command
	@log_command
	def command_cli(self, update, context):
		args_list = ["--telegram"] + shlex.split(' '.join(context.args))
		self.send_text(
			TimeCsv.cli.main(self.datafolder, args_list),
			update
		)

	#
	# text report
	#
	def filtered_time_command(self, f, update=None):
		g = GroupedStats_Group(
			f % self.datafolder.data,
			selected_time=f.get_selected_time(),
			group_value="time"
		)

		self.send_text(
			g.to_telegram(),
			update
		)

	@whitelisted_command
	@log_command
	def command_text_report(self, update, context):
		def kbd(name):
			return InlineKeyboardButton(name, callback_data=f"menu_text_report {name}")

		keyboard = [
			[kbd("today"), kbd("yesterday"), kbd("week"), kbd("last_week")],
			[kbd("month"), kbd("year"), kbd("all")],
		]
		update.message.reply_text(
			"Select date:",
			reply_markup=InlineKeyboardMarkup(keyboard)
		)

	@whitelisted_command
	@log_command
	def menu_text_report(self, update, context):
		data = update.callback_query.data
		callback_name, filter_name = data.split()

		self.filtered_time_command(
			get_named_filter(filter_name),
			update
		)


	@whitelisted_command
	@log_command
	def command_text_report_month(self, update=None, context=None):
		month, year = self.parse_args(context, int, int)
		self.filtered_time_command(TimeFilter_Month(month, year), update)

	@whitelisted_command
	@log_command
	def command_text_report_year(self, update=None, context=None):
		year, = self.parse_args(context, int)
		self.filtered_time_command(TimeFilter_Year(year), update)

	#
	# pie reports
	#
	def pie_command(self, g_cls, f, update=None):
		g = g_cls(
			f % self.datafolder.data,
			selected_time=f.get_selected_time(),
			group_value="time"
		)

		# TODO:
		# this initializes self.headers_sorted, self.values_sorted
		# there should be a better (and automated) way to initialize them
		g.group()

		pie_file = g.to_pie()

		self.send_image(pie_file, update)

	MENU_PIE_SUBJECTS = {
		"homework" : GroupedStats_Homework,
		"lecture"  : GroupedStats_Lecture,
		"gaming"   : GroupedStats_Games,
		"youtube"  : GroupedStats_Youtube,
	}

	@whitelisted_command
	@log_command
	def command_pie(self, update, context):
		def kbd(name):
			return InlineKeyboardButton(name, callback_data=f"menu_pie {name}")

		keyboard = [
			[kbd(i) for i in self.MENU_PIE_SUBJECTS.keys()],
		]
		update.message.reply_text(
			"Select subject:",
			reply_markup=InlineKeyboardMarkup(keyboard)
		)

	@whitelisted_command
	@log_command
	def menu_pie(self, update, context):
		data = update.callback_query.data
		callback_name, subject_name = data.split()

		self.pie_command(
			self.MENU_PIE_SUBJECTS[subject_name],
			TimeFilter_Days(7),
			update
		)

	#
	# productive pie
	#
	@whitelisted_command
	@log_command
	def command_productive_pie(self, update, context):
		focused, = self.parse_args(context, int) # taking a boolean value as int. Expecting only 0 or 1.

		def kbd(name):
			return InlineKeyboardButton(name, callback_data=f"menu_productive_pie {name} {focused}")

		keyboard = [
			[kbd("today"), kbd("yesterday"), kbd("week"), kbd("last_week")],
			[kbd("month"), kbd("year"), kbd("all")],
		]
		update.message.reply_text(
			"Select date:",
			reply_markup=InlineKeyboardMarkup(keyboard)
		)

	@whitelisted_command
	@log_command
	def menu_productive_pie(self, update, context):
		data = update.callback_query.data
		callback_name, filter_name, focused = data.split()

		f = get_named_filter(filter_name)
		focused = bool(int(focused))

		pie_file = get_productivity_pie(
			data=f % self.datafolder.data,
			selected_time=filter_name,
			save=True,
			focused=focused
		)

		self.send_image(pie_file, update)


	@whitelisted_command
	@log_command
	def command_productive_pie_month(self, update=None, context=None):
		month, year, focused = self.parse_args(context, int, int, int)
		f = TimeFilter_Month(month, year)

		pie_file = get_productivity_pie(
			data=f % self.datafolder.data,
			selected_time=f._selected_time,
			save=True,
			focused=bool(focused)
		)

		self.send_image(pie_file, update)

	@whitelisted_command
	@log_command
	def command_productive_pie_year(self, update=None, context=None):
		year, focused = self.parse_args(context, int, int)
		f = TimeFilter_Year(year)

		pie_file = get_productivity_pie(
			data=f % self.datafolder.data,
			selected_time=f._selected_time,
			save=True,
			focused=bool(focused)
		)

		self.send_image(pie_file, update)

	#
	# others
	#
	@whitelisted_command
	@log_command
	def command_test(self, update=None, context=None):
		s = "test"
		if context.args:
			s += ": " + str(context.args)
		self.send_text(s, update)

	@whitelisted_command
	@log_command
	def command_pdb(self, update=None, context=None):
		pdb.set_trace()

	@whitelisted_command
	@log_command
	def command_reload(self, update=None, context=None):
		self.datafolder.reload()
		log(f"    [r] reloaded : {time.asctime()}")

		# if update is None - we are called from the scheduler
		# only answer the user if the user asks the reload
		if update is not None:
			self.send_text("reload - done", update)

	@whitelisted_command
	@log_command
	def command_wget(self, update=None, context=None):
		wget(log, update, context)

		# if update is None - we are called from the scheduler
		# only answer the user if the user asks the reload
		if update is not None:
			self.send_text(f"wget - done\n{get_wget_log()}", update)

		wget_only, = self.parse_args(context, int)
		if not bool(wget_only):
			self.command_reload(update, context)

	def full_reload(self):
		self.command_wget()
		self.command_reload()

	@log_command
	def command_list_commands(self, update=None, context=None):
		commands = filter(
			lambda s: s.startswith("command_"),
			dir(self)
		)

		self.send_text(
			'\n'.join(
				f"{self._command_name(c)} - {self._command_name(c)}"
				for c in commands
			),
			update
		)

class TelegramScheduledCommands(object):
	def schedule_commands(self):
		#
		# daily log
		#
		# yesterday text report
		schedule.every().day.at("08:00").do(
			self.filtered_time_command,
			get_named_filter("yesterday"),
		)
		# yesterday productive pie
		schedule.every().day.at("08:00").do(
			self.send_image,
			get_productivity_pie(
				data=get_named_filter("yesterday") % self.datafolder.data,
				selected_time="yesterday",
				save=True,
				focused=False
			)
		)

		# weekly log
		#
		# last week text report
		schedule.every().sunday.at("08:00").do(
			self.filtered_time_command,
			get_named_filter("last_week"),
		)
		# weekly productive pie
		schedule.every().sunday.at("08:00").do(
			self.send_image,
			get_productivity_pie(
				data=get_named_filter("last_week") % self.datafolder.data,
				selected_time="last_week",
				save=True,
				focused=False
			)
		)
		# homework pie
		schedule.every().sunday.at("08:00").do(
			self.pie_command,
			GroupedStats_Homework,
			TimeFilter_Days(7),
		)
		# gaming pie
		schedule.every().sunday.at("08:00").do(
			self.pie_command,
			GroupedStats_Games,
			TimeFilter_Days(7),
		)

		# reload
		schedule.every().day.at("06:00").do(
			self.full_reload
		)


		def run_scheduler():
			while True:
				try:
					schedule.run_pending()
					time.sleep(60*60*0.5)

				except ParseError as pe:
					# log error to screen + log file
					log(f"[*] Caught ParseError in run_scheduler. retrying in {RETRY_SLEEP_AMOUNT_IN_HOURS} hours")
					log(f"Caught ParseError:\n{str(pe)}")
					# send error to the main user
					self.send_text(f"Caught ParseError:\n{str(pe)}")
					# re-sync with dropbox
					time.sleep(RETRY_SLEEP_AMOUNT_IN_HOURS * 60 * 60)
					self.command_reload(scheduled=True)

				except Exception as exc:
					log(f"[!] Caught general error in run_scheduler - quitting")

					exc_type, exc_value, exc_traceback = sys.exc_info()
					lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
					exception_message = ''.join('!! ' + line for line in lines)  # Log it or whatever here
					log(exception_message)

					raise exc

		threading.Thread(target=run_scheduler).start()


class TelegramAPI(TelegramServer, TelegramCommands, TelegramScheduledCommands):
	def __init__(self):
		super().__init__()
		self.add_all_handlers()
		self.schedule_commands()

def main():
	log(f"----------------")
	now = datetime.datetime.now().strftime("%Y/%m/%d_%H:%M")
	log(f"[*] Starting: {now}")

	while True:
		try:
			# an exception can either happen in __init__, when self.datafolder is created
			t = TelegramAPI()
			# or in loop, where the `reload` method is called
			t.loop()

		except ParseError as pe:
			log(f"[*] Caught ParseError in main. retrying in {RETRY_SLEEP_AMOUNT_IN_HOURS} hours")
			log(f"Caught ParseError:\n{str(pe)}")
			time.sleep(RETRY_SLEEP_AMOUNT_IN_HOURS * 60 * 60)
			os.system(DAILY_WGET_PATH)

		except Exception as exc:
			log(f"[!] Caught general error in main - quitting")

			exc_type, exc_value, exc_traceback = sys.exc_info()
			lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			exception_message = ''.join('!! ' + line for line in lines)  # Log it or whatever here
			log(exception_message)

			raise exc
	LOG_FILE.close()

"""
# all commands:
text_report - text_report
pie - pie
productive_pie - productive_pie

reload - reload

month - month
year - year

productive_pie_month - productive_pie_month
productive_pie_year - productive_pie_year

list_commands - list_commands
cli - cli
test - test
pdb - pdb
"""

if __name__ == '__main__':
	main()
