import os
import pdb
import time
import shlex

import TimeCsv.cli
from TimeCsv.parsing import DataFolder

from TimeCsv.consts import *
from TimeCsv.filters import *

from telegram.ext import Updater, InlineQueryHandler, CommandHandler


# utils
def read_file(filename):
	return open(os.path.join(
		TELEGRAM_DATA_DIRECTORY,
		filename
	)).read().strip()

def log_command(func):
	def func_wrapper(*args, **kwargs):
		# each function is named "command_something"
		command_name = func.__name__[8:]
		print(f"[*] got command - {args[1]['message']['text']}\tcalling {command_name}\t{time.asctime()}")
		return func(*args, **kwargs)

	return func_wrapper


class TelegramServer(object):
	def __init__(self):
		# server initialization
		self._key = read_file("key")
		self._chat_id = int(read_file("chat_id"))

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
		print("[*] entering loop")
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

	@log_command
	def command_cli(self, update, context):
		args_list = ["--telegram"] + shlex.split(' '.join(context.args))
		self.send_text(
			TimeCsv.cli.main(self.datafolder, args_list),
			update
		)

	#
	def filtered_time_command(self, f, update=None):
		g = TimeCsv.statistics.GroupedStats_Group(
			f % self.datafolder.data,
			selected_time=f.get_selected_time(),
			group_value="time"
		)

		self.send_text(
			g.to_telegram(),
			update
		)

	@log_command
	def command_today(self, update, context):
		self.filtered_time_command(TimeFilter_Days(1), update)

	@log_command
	def command_week(self, update, context):
		self.filtered_time_command(TimeFilter_Days(7), update)

	@log_command
	def command_month(self, update, context):
		if context.args:
			try:
				month = int(context.args[0])
			except Exception as e:
				self.send_text(f"command_month error: {e}", update)
		else:
			month = 0 # the default value

		self.filtered_time_command(TimeFilter_Month(month), update)

	@log_command
	def command_year(self, update, context):
		if context.args:
			try:
				year = int(context.args[0])
			except Exception as e:
				self.send_text(f"command_year error: {e}", update)
		else:
			year = 0 # the default value

		self.filtered_time_command(TimeFilter_Year(year), update)

	@log_command
	def command_yesterday(self, update, context):
		stop_time  = get_midnight( datetime.datetime.now() )
		start_time = get_midnight(
			stop_time
			 -
			datetime.timedelta(days=1)
		)

		self.filtered_time_command(
			TimeFilter_DateRange(
				start_time,
				stop_time
			),
			update
		)

	@log_command
	def command_last_week(self, update, context):
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
			TimeFilter_DateRange(
				prev_sunday,
				this_sunday
			),
			update
		)

	#
	@log_command
	def command_test(self, update, context):
		s = "test"
		if context.args:
			s += ": " + str(context.args)
		self.send_text(s, update)

	@log_command
	def command_pdb(self, update, context):
		pdb.set_trace()

	@log_command
	def command_reload(self, update, context):
		self.datafolder.reload()
		self.send_text("done", update)

	@log_command
	def command_list_commands(self, update, context):
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

"""
TODO:
add homework command
which sends a pie chart
"""

class TelegramAPI(TelegramServer, TelegramCommands):
	def __init__(self):
		super().__init__()
		self.add_all_handlers()

def main():
	t = TelegramAPI()
	t.loop()

if __name__ == '__main__':
	main()