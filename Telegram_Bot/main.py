#!/usr/bin/env python3
import math
import logging
import schedule
from collections import ChainMap

from TimeCsv import DetailedStats_AllGroups  , \
					DetailedStats_Read       , \
					DetailedStats_ReadBook   , \
					DetailedStats_Lecture    , \
					DetailedStats_Life       , \
					DetailedStats_PrepareFood, \
					DetailedStats_Homework   , \
					DetailedStats_Games      , \
					DetailedStats_Youtube    , \
					TimeFilter_Month   , \
					TimeFilter_Year    , \
					TimeFilter_ThisWeek, \
					DataFolder
from TimeCsv.functions.productivity import get_productivity_pie
from TimeCsv.Telegram_Bot.telegram_bot_template import TelegramSecureServer, TelegramCommands, TelegramScheduledCommands
from TimeCsv.Telegram_Bot.utils import initialize_logger, get_named_filter

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# from TelegramBots.consts import *
# from TelegramBots.utils import *
# from TelegramBots.wrappers import *
# from TelegramBots.telegram_bot_template import *


class TimeCsvCommands(TelegramCommands):
	#
	# Text commands
	#
	def _allgroups_textual(self, time_filter, update=None):
		stats = DetailedStats_AllGroups(
			time_filter % self.datafolder.data,
			time_filter,
			grouping_method="time",
		)
		self.send_text(
			stats.to_telegram(),
			update
		)

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

	def menu_text_report(self, update, context):
		data = update.callback_query.data
		callback_name, filter_name = data.split()

		self._allgroups_textual(
			get_named_filter(filter_name),
			update
		)

	def command_text_report_month(self, update=None, context=None):
		month, year = self.parse_args(context, int, int)
		self._allgroups_textual(TimeFilter_Month(month, year), update)

	def command_text_report_year(self, update=None, context=None):
		year, = self.parse_args(context, int)
		self._allgroups_textual(TimeFilter_Year(year), update)

	#
	# Pie commands
	#
	def _pie(self, stats_cls, time_filter, update=None):
		stats = stats_cls(
			time_filter % self.datafolder.data,
			time_filter=time_filter,
			grouping_method="time",
		)

		pie_file = stats.to_pie()

		self.send_image(pie_file, update)

	MENU_PIE_SUBJECTS = [
		{
			"read"        : DetailedStats_Read,
			"readbook"    : DetailedStats_ReadBook,
			"lecture"     : DetailedStats_Lecture,
		}, {
			"life"        : DetailedStats_Life,
			"preparefood" : DetailedStats_PrepareFood,
			"homework"    : DetailedStats_Homework,
		}, {
			"gaming"      : DetailedStats_Games,
			"youtube"     : DetailedStats_Youtube,
		}
	]

	def command_pie(self, update, context):
		def kbd(name):
			return InlineKeyboardButton(name, callback_data=f"menu_pie {name}")

		keyboard = [
			[kbd(i) for i in subjects.keys()]
			for subjects in self.MENU_PIE_SUBJECTS
		]
		update.message.reply_text(
			"Select subject:",
			reply_markup=InlineKeyboardMarkup(keyboard)
		)

	def menu_pie(self, update, context):
		data = update.callback_query.data
		callback_name, subject_name = data.split()

		self._pie(
			# combine all the dicts, and get the relevant one
			dict(ChainMap(*self.MENU_PIE_SUBJECTS))[subject_name],
			TimeFilter_ThisWeek(),
			update
		)

	#
	# Productive Pie
	#
	def _productive_pie(self, time_filter, update=None, **kwargs):
		pie_file = get_productivity_pie(
			data=time_filter % self.datafolder.data,
			save=True,
			**kwargs
		)

		self.send_image(pie_file, update)

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

	def menu_productive_pie(self, update, context):
		data = update.callback_query.data
		callback_name, filter_name, focused = data.split()

		self._productive_pie(
			get_named_filter(filter_name),
			focused=bool(int(focused)),
			update=update,
		)

	def command_productive_pie_month(self, update=None, context=None):
		month, year, focused = self.parse_args(context, int, int, int)
		time_filter = TimeFilter_Month(month, year)

		self._productive_pie(
			time_filter,
			focused=bool(focused),
			update=update,
		)

	def command_productive_pie_year(self, update=None, context=None):
		year, focused = self.parse_args(context, int, int)
		time_filter = TimeFilter_Year(year)

		self._productive_pie(
			time_filter,
			focused=bool(focused),
			update=update,
		)

	#
	# Debug
	#
	def command_reload(self, update=None, context=None):
		self.datafolder.reload()
		logging.info("[r] reloaded")

		# if update is None - we are called from the scheduler
		# only answer the user if the user asks the reload
		if update is not None:
			self.send_text("reload - done", update)

	def command_test(self, update=None, context=None):
		s = "test"
		if context is not None and context.args:
			s += ": " + str(context.args)
		self.send_text(s, update)

	def command_pdb(self, update=None, context=None):
		pdb.set_trace()



class TimeCsvScheduledCommands(TelegramScheduledCommands):
	def schedule_hourly(self):
		schedule.every().hour.at(":57").do(
			self.command_reload,
			scheduled=True
		)

	def schedule_daily(self):
		# yesterday text report
		schedule.every().day.at("08:00").do(
			self._allgroups_textual,
			get_named_filter("yesterday"),
		)
		# yesterday productive pie

	def schedule_weekly(self):
		#
		# weekly log
		#
		# last week text report
		schedule.every().sunday.at("08:00").do(
			self._allgroups_textual,
			get_named_filter("last_week"),
		)
		# # weekly productive pie
		# schedule.every().sunday.at("08:00").do(
		# 	self.send_image,
		# 	get_productivity_pie(
		# 		data=get_named_filter("last_week") % self.datafolder.data,
		# 		selected_time="last_week",
		# 		save=True,
		# 		focused=False
		# 	)
		# )

class TimeCsvTelegramAPI(
		TelegramSecureServer,
		TimeCsvCommands,
		TimeCsvScheduledCommands
	):
	def __init__(self, datafolder=None):
		self.datafolder = datafolder or DataFolder()

		# TelegramSecureServer
		super().__init__()
		# TelegramCommandsExamples
		self.add_all_handlers()
		# TelegramScheduledCommands
		self.schedule_commands()
		self.start_scheduler()


def test():
	initialize_logger(debug=True)

	t = TimeCsvTelegramAPI()
	# t.loop()
	t.loop_no_error()


if __name__ == '__main__':
	test()
