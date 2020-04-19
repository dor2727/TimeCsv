import os
import pdb
import time
import shlex

import TimeCsv.cli
from TimeCsv.parsing import DataFolder

from TimeCsv.consts import *

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
	def add_all_handlers(self):
		commands = filter(
			lambda s: s.startswith("command_"),
			dir(self)
		)

		for command_name in commands:
			self.dp.add_handler(CommandHandler(
				command_name[8:],
				getattr(self, command_name)
			))

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
	def command_cli(self, update, context):
		args_list = ["--telegram"] + shlex.split(' '.join(context.args))
		self.send_text(
			TimeCsv.cli.main(self.datafolder, args_list),
			update
		)


class TelegramAPI(TelegramServer, TelegramCommands):
	def __init__(self):
		super().__init__()
		self.add_all_handlers()

"""
TODO
add all handlers
how?
1)
	def add_all_handlers(self):
		for i in seld.__dict__:
			if key(i).startswith("command_"):
				self.dp.add_handler(CommandHandler('start', start))
2)
	@add_handler

	def add_handler(func, handler_name=None):
		func.__self__.dp.add_handler(CommandHandler('start', start))
		return func
"""

def main():
	t = TelegramAPI()
	t.loop()

if __name__ == '__main__':
	main()