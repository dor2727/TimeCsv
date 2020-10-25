#!/usr/bin/env python3
import os
import pdb
import time
import shlex
import schedule
import threading

import TimeCsv.cli
from TimeCsv.parsing import DataFolder, ParseError

from TimeCsv.consts import *
from TimeCsv.filters import *
from TimeCsv.statistics import *
from TimeCsv.time_utils import read_telegram_file, log
from TimeCsv.functions.productivity import get_productivity_pie

from telegram.ext import Updater, InlineQueryHandler, CommandHandler


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
				command_text = args[1]['message']['text']
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
			chat_id = update['message']['chat']['id']
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
			return update['message']['chat']['id']
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
		commands = filter(
			lambda s: s.startswith("command_"),
			dir(self)
		)

		for command_name in commands:
			self.dp.add_handler(CommandHandler(
				self._command_name(command_name),
				getattr(self, command_name)
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
	def command_today(self, update=None, context=None):
		self.filtered_time_command(TimeFilter_Days(1), update)

	@whitelisted_command
	@log_command
	def command_week(self, update=None, context=None):
		self.filtered_time_command(TimeFilter_Days(7), update)

	@whitelisted_command
	@log_command
	def command_month(self, update=None, context=None):
		month, year = self.parse_args(context, int, int)
		self.filtered_time_command(TimeFilter_Month(month, year), update)

	@whitelisted_command
	@log_command
	def command_year(self, update=None, context=None):
		year, = self.parse_args(context, int)
		self.filtered_time_command(TimeFilter_Year(year), update)

	@whitelisted_command
	@log_command
	def command_yesterday(self, update=None, context=None):
		stop_time  = get_midnight( datetime.datetime.now() )
		start_time = get_midnight(
			stop_time
			 -
			datetime.timedelta(days=1)
		)

		self.filtered_time_command(
			TimeFilter_DateRange( start_time, stop_time ),
			update
		)

	@whitelisted_command
	@log_command
	def command_last_week(self, update=None, context=None):
		today = datetime.datetime.now()

		if WEEK_STARTS_AT_SUNDAY:
			weekday = today.weekday() + WEEK_STARTS_AT_SUNDAY
			if weekday == 7:
				weekday = 0
		else:
			weekday = today.weekday()
		this_sunday = get_midnight(today - datetime.timedelta(days=weekday))
		prev_sunday = this_sunday - datetime.timedelta(days=7)

		self.filtered_time_command(
			TimeFilter_DateRange( prev_sunday, this_sunday ),
			update
		)

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

	@whitelisted_command
	@log_command
	def command_homework_pie(self, update=None, context=None):
		self.pie_command(GroupedStats_Homework, TimeFilter_Days(7), update)

	@whitelisted_command
	@log_command
	def command_lecture_pie(self, update=None, context=None):
		self.pie_command(GroupedStats_Lecture, TimeFilter_Days(7), update)

	@whitelisted_command
	@log_command
	def command_gaming_pie(self, update=None, context=None):
		self.pie_command(GroupedStats_Games, TimeFilter_Days(7), update)

	@whitelisted_command
	@log_command
	def command_youtube_pie(self, update=None, context=None):
		self.pie_command(GroupedStats_Youtube, TimeFilter_Days(7), update)


	#
	@whitelisted_command
	@log_command
	def command_productive_pie_today(self, update=None, context=None):
		focused, = self.parse_args(context, int) # taking a boolean value as int. Expecting only 0 or 1.
		f = TimeFilter_Days(1)

		pie_file = get_productivity_pie(
			data=f % self.datafolder.data,
			selected_time=f._selected_time,
			save=True,
			focused=bool(focused)
		)

		self.send_image(pie_file, update)

	@whitelisted_command
	@log_command
	def command_productive_pie_yesterday(self, update=None, context=None):
		focused, = self.parse_args(context, int) # taking a boolean value as int. Expecting only 0 or 1.

		stop_time  = get_midnight( datetime.datetime.now() )
		start_time = get_midnight(
			stop_time
			 -
			datetime.timedelta(days=1)
		)

		f = TimeFilter_DateRange( start_time, stop_time )

		pie_file = get_productivity_pie(
			data=f % self.datafolder.data,
			selected_time=f._selected_time,
			save=True,
			focused=bool(focused)
		)

		self.send_image(pie_file, update)

	@whitelisted_command
	@log_command
	def command_productive_pie_week(self, update=None, context=None):
		focused, = self.parse_args(context, int) # taking a boolean value as int. Expecting only 0 or 1.

		f = TimeFilter_Days(7)

		pie_file = get_productivity_pie(
			data=f % self.datafolder.data,
			selected_time=f._selected_time,
			save=True,
			focused=bool(focused)
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

	@whitelisted_command
	@log_command
	def command_productive_pie_all(self, update=None, context=None):
		focused, = self.parse_args(context, int) # taking a boolean value as int. Expecting only 0 or 1.

		pie_file = get_productivity_pie(
			data=self.datafolder.data,
			save=True,
			focused=bool(focused)
		)

		self.send_image(pie_file, update)


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
		# daily log
		schedule.every().day.at("08:00").do(
			self.command_yesterday,
			scheduled=True
		)
		schedule.every().day.at("08:00").do(
			self.command_productive_pie_yesterday,
			scheduled=True
		)
		
		# weekly log
		schedule.every().sunday.at("08:00").do(
			self.command_last_week,
			scheduled=True
		)
		schedule.every().sunday.at("08:00").do(
			self.command_productive_pie_week,
			scheduled=True
		)
		
		# weekly pies
		# schedule.every().sunday.at("08:00").do(
		# 	self.command_homework_pie,
		# 	scheduled=True
		# )

		schedule.every().sunday.at("08:00").do(
			self.command_gaming_pie,
			scheduled=True
		)

		schedule.every().hour.at(":57").do(
			self.command_reload,
			scheduled=True
		)


		def run_scheduler():
			while True:
				schedule.run_pending()
				time.sleep(60*60*0.5)

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
			time.sleep(RETRY_SLEEP_AMOUNT_IN_HOURS * 60 * 60)

		except Exception as exc:
			log(f"[!] Caught general error in main - quitting")
			raise exc
	LOG_FILE.close()

"""
# all commands:
today - today
yesterday - yesterday
week - week
last_week - last_week
month - month
year - year

reload - reload

productive_pie_today - productive_pie_today
productive_pie_yesterday - productive_pie_yesterday
productive_pie_week - productive_pie_week
productive_pie_month - productive_pie_month
productive_pie_year - productive_pie_year
productive_pie_all - productive_pie_all

gaming_pie - gaming_pie
homework_pie - homework_pie
lecture_pie - lecture_pie
youtube_pie - youtube_pie

list_commands - list_commands
cli - cli
test - test
pdb - pdb
"""

if __name__ == '__main__':
	main()