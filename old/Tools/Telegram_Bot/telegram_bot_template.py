import time
import socket
import logging
import threading
import schedule
import http

from TimeCsv.Telegram_Bot.consts import KEY_FILEPATH, CHAT_ID_FILEPATH
from TimeCsv.Telegram_Bot.wrappers import wrapper_log, wrapper_log_secure, wrapper_whitelist
from TimeCsv.Telegram_Bot.utils import *
# from TelegramBots.consts import *
# from TelegramBots.utils import *
# from TelegramBots.wrappers import *

# from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import telegram # telegram.error.NetworkError, telegram.vendor.ptb_urllib3.urllib3.exceptions.ProtocolError


class TelegramServer(object):
	_wrappers = [wrapper_log]
	def __init__(self):
		self.updater = Updater(
			read_file(KEY_FILEPATH),
			use_context=True
		)

	@property
	def dp(self):
		return self.updater.dispatcher

	def chat_id(self, update):
		return get_chat_id(update)

	def send_text(self, text, update, **kwargs):
		self.updater.bot.sendMessage(
			self.chat_id(update),
			text,
			**kwargs
		)

	def send_image(self, image_file, update, **kwargs):
		self.updater.bot.send_photo(
			self.chat_id(update),
			photo=image_file,
			**kwargs
		)

	def loop(self):
		logging.info("Entering loop")
		self.updater.start_polling(timeout=123)
		self.updater.idle()

	def loop_no_error(self):
		while True:
			try:
				self.loop()

			# socket.gaierror: [Errno -3] Temporary failure in name resolution
			except socket.gaierror as exc:
				if exc.errno == -3:
					logging.warning(f"[*] Caught socket.gaierror (-3) in main (loop) - continue")
				else:
					logging.warning(f"[*] Caught socket.gaierror ({exc.errno}) in main (loop) - continue")
					logging.warning(str(exc))

				continue

			except telegram.error.NetworkError as exc:
				logging.warning(f"[*] Caught telegram.error.NetworkError ({str(exc)}) in main (loop) - continue")
				continue

			except telegram.vendor.ptb_urllib3.urllib3.exceptions.ProtocolError as exc:
				logging.warning(f"[*] Caught telegram.vendor.ptb_urllib3.urllib3.exceptions.ProtocolError ({str(exc)}) in main (loop) - continue")
				continue

			except http.client.RemoteDisconnected as exc:
				logging.warning(f"[*] Caught http.client.RemoteDisconnected ({str(exc)}) in main (loop) - continue")
				continue

			except Exception as exc:
				logging.warning(f"[!] Caught general error in main (loop) - quitting")
				logging.warning(exception_message())
				raise exc


class TelegramSecureServer(TelegramServer):
	# log first, then check the whitelist (so that 'bad' calls are logged)
	_wrappers = [wrapper_log_secure, wrapper_whitelist]

	# _MAIN_USER may have one of the following values:
	# 1) None - no main user
	# 2) a string - the name of the main user
	# 3) a number - the chat_id of the main user
	_MAIN_USER = None

	def __init__(self):
		super().__init__()

		self._get_all_users()
		self._print_all_users()

	def _get_all_users(self):
		if os.path.isdir(CHAT_ID_FILEPATH):
			files = filter(
				is_chat_id,
				get_folder_files(CHAT_ID_FILEPATH)
			)
		elif os.path.isfile(CHAT_ID_FILEPATH):
			files = [CHAT_ID_FILEPATH]
		else:
			raise ValueError(f"Invalid CHAT_ID_FILEPATH ({CHAT_ID_FILEPATH})")

		self.user_names    = []
		self.user_chat_ids = []

		for f in files:
			self.user_names.append(get_chat_id_username(f))
			self.user_chat_ids.append(get_chat_id_from_file_name(f))

		self.users = dict(zip(self.user_names, self.user_chat_ids))

	def _print_all_users(self):
		logging.info("Current users:")
		for i in range(len(self.user_chat_ids)):
			logging.info(f"    {i}) {self.user_names[i]} - {self.user_chat_ids[i]}")

	@property
	def MAIN_USER(self):
		if type(self._MAIN_USER) is int:
			if self._MAIN_USER in self.user_chat_ids:
				return self._MAIN_USER
			else:
				logging.error(f"MAIN_USER ({self._MAIN_USER}) not in user_chat_ids ({str(self.user_chat_ids)})")
				raise ValueError("MAIN_USER is not a registered user")

		elif type(self._MAIN_USER) is str:
			if self._MAIN_USER in self.user_names:
				return self.users[self._MAIN_USER]
			else:
				logging.error(f"MAIN_USER ({self._MAIN_USER}) not in user_names ({str(self.user_names)})")
				raise ValueError("MAIN_USER is not a registered user")

		elif self._MAIN_USER is None:
			raise ValueError("MAIN_USER was accessed, yet no MAIN_USER was defined")

		else:
			logging.error(f"MAIN_USER = {type(self._MAIN_USER)} : {str(self._MAIN_USER)}")
			raise NotImplemented("An invalid value for self.MAIN_USER was given")

	# changing function declaration - allowing `update` to be None - meaning the MAIN_USER
	def chat_id(self, update=None):
		if update:
			return super().chat_id(update)
		else:
			return self.MAIN_USER

	def send_text(self, text, update=None, **kwargs):
		super().send_text(text, update, **kwargs)

	def send_image(self, image_file, update=None, **kwargs):
		super().send_image(image_file, update, **kwargs)



class TelegramCommands(object):
	def _get_all_command_names(self):
		return filter(
			is_command_name,
			dir(self)
		)
	def _get_all_menu_names(self):
		return filter(
			is_menu_name,
			dir(self)
		)

	def add_all_handlers(self):
		def wrap(func):
			func_name = func.__name__
			# innermost wrapper is the last in the list
			for w in self._wrappers[::-1]:
				func = w(func, self=self, func_name=func_name)
			return func

		# register commands
		for command_name in self._get_all_command_names():
			self.dp.add_handler(
				CommandHandler(
					strip_command_name(command_name),
					wrap( getattr(self, command_name) )
				)
			)
		# register menus
		for menu_name in self._get_all_menu_names():
			self.dp.add_handler(
				CallbackQueryHandler(
					wrap( getattr(self, menu_name) ),
					pattern=generate_menu_patter(menu_name),
				)
			)

	def parse_args(self, context, *expected_types):
		result = []
		if context and context.args:
			try:
				for i in range(len(context.args)):
					result.append(expected_types[i](context.args[i]))
			except Exception as e:
				self.send_text(
					f"parse_args error: {e} ; args = {context.args}",
					# send it to me, not to the user (avoiding information disclosure)
					self.chat_id()
				)

		# fill default values, if needed
		for i in range(len(result), len(expected_types)):
			result.append(expected_types[i]())

		return result

	# Usefull for setting bot commands in the BotFather
	def command_list_commands(self, update=None, context=None):
		self.send_text(
			'\n'.join(
				f"{strip_command_name(c)} - {strip_command_name(c)}"
				for c in self._get_all_command_names()
			),
			update
		)

class TelegramScheduledCommands(object):
	def schedule_commands(self):
		self.schedule_hourly()
		self.schedule_daily()
		self.schedule_weekly()

	def schedule_hourly(self):
		pass

	def schedule_daily(self):
		pass

	def schedule_weekly(self):
		pass

	def start_scheduler(self):
		def run_scheduler():
			while True:
				try:
					schedule.run_pending()
					time.sleep(SCHEDULER_SLEEP_AMOUNT_IN_SECONDS)

				# socket.gaierror: [Errno -3] Temporary failure in name resolution
				except socket.gaierror as exc:
					if exc.errno == -3:
						logging.warning(f"[*] Caught socket.gaierror (-3) in main (loop) - continue")
					else:
						logging.warning(f"[*] Caught socket.gaierror ({exc.errno}) in main (loop) - continue")
						logging.warning(str(exc))

					continue

				except telegram.error.NetworkError as exc:
					logging.warning(f"[*] Caught telegram.error.NetworkError ({str(exc)}) in run_scheduler - continue")
					continue

				except telegram.vendor.ptb_urllib3.urllib3.exceptions.ProtocolError as exc:
					logging.warning(f"[*] Caught telegram.vendor.ptb_urllib3.urllib3.exceptions.ProtocolError ({str(exc)}) in run_scheduler - continue")
					continue

				except http.client.RemoteDisconnected as exc:
					logging.warning(f"[*] Caught http.client.RemoteDisconnected ({str(exc)}) in run_scheduler - continue")
					continue

				except Exception as exc:
					log(f"[!] Caught general error in run_scheduler - quitting")
					log(exception_message())
					raise exc

		threading.Thread(target=run_scheduler).start()
