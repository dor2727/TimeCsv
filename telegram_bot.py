#!/usr/local/bin/python3.7

import threading
import time
import schedule
import Time.statistics
from telegram.ext import Updater, InlineQueryHandler, CommandHandler

from pdb import set_trace

MY_CHAT_ID = int(open('chat_id').read().strip())

FILENAME = "/home/me/Dropbox/Projects/Time/data/2020_year_2_semester_1.tcsv"
FILENAME = Time.statistics.newest(Time.statistics.DEFAULT_DATA_FOLDER)

MY_TIME_DATA = None
MY_BOT_API   = None


def log_command(s):
	print(f"[*] got command - {s}\t{time.asctime()}")


# handlers
def test(message, update):
	log_command("test")
	chat_id = message['message']['chat']['id']
	update.bot.sendMessage(chat_id, "test")

def pdb(message, update):
	log_command("pdb")
	set_trace()

def start(message, update):
	global MY_CHAT_ID
	MY_CHAT_ID = message['message']['chat']['id']
	print(f"[*] start - {MY_CHAT_ID}")
	

# initialization funcitons
def init_time_data():
	print(f"[*] initializing time data : {FILENAME.split('/')[-1]}")
	global MY_TIME_DATA
	global MY_BOT_API
	MY_TIME_DATA = Time.statistics.TimeParser(path=FILENAME)
	MY_BOT_API   = Time.statistics.TelegramBotAPI(MY_TIME_DATA.get_data)

def init_telegram():
	print("[*] connecting to telegram")
	key = open('key').read().strip()
	updater = Updater(key, use_context=True)
	return updater

def add_handlers_basic(dp):
	print("[*] adding handlers - basic")
	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(CommandHandler('test',test))
	dp.add_handler(CommandHandler('pdb',pdb))

def reload_csv(message, update):
	log_command("reload")
	MY_TIME_DATA.reload()
	chat_id = message['message']['chat']['id']
	update.bot.sendMessage(chat_id, "done")


def add_handlers_time(dp):
	print("[*] adding handlers - time")
	for i in ("last_day", "last_week", "current_week", "today"):
		dp.add_handler(CommandHandler(
			i,
			MY_BOT_API.create_bot_command(i)
		))
		dp.add_handler(CommandHandler(
			i + "_full",
			MY_BOT_API.create_bot_command(i, full_report=True)
		))

	dp.add_handler(CommandHandler('reload',reload_csv))

def add_homework_handler(dp):
	dp.add_handler(CommandHandler(
		"homework_pie",
		MY_BOT_API.create_homework_pie_command()
	))
	dp.add_handler(CommandHandler(
		"homework_pie_amount",
		MY_BOT_API.create_homework_pie_command(True)
	))

	dp.add_handler(CommandHandler(
		"homework_text",
		MY_BOT_API.create_homework_text_command()
	))
	dp.add_handler(CommandHandler(
		"homework_text_amount",
		MY_BOT_API.create_homework_text_command(True)
	))

	


# schedualing functions
def send_message(updater, text):
	updater.bot.sendMessage(MY_CHAT_ID, text)
def send_report(updater, report_name, full_report=False):
	reporters = Time.statistics.FULL_REPORTERS if full_report else None

	report_data = MY_BOT_API.create_report(report_name, reporters=reporters)

	report_text = report_name + '\n' + '\n'.join(report_data)
	send_message(updater, report_text)

def schedule_tasks(updater):
	daily  = lambda : send_report(updater, "last_day", full_report=True)
	schedule.every().day.at("08:00").do(daily)

	weekly = lambda : send_report(updater, "last_week", full_report=True)
	schedule.every().sunday.at("08:00").do(weekly)

	def hourly_reload():
		MY_TIME_DATA.reload()
		print(f"reloaded : {time.asctime()}")
	schedule.every().hour.at(":57").do(hourly_reload)

	def weekly_pie():
		f = MY_BOT_API.create_homework_pie_command()
		message = {}
		message['message'] = {}
		message['message']['chat'] = {}
		message['message']['chat']['id'] = MY_CHAT_ID
		f(message, updater)
	schedule.every().sunday.at("08:00").do(weekly_pie)


	def run_scheduler():
		while True:
			schedule.run_pending()
			time.sleep(60*60*0.5)

	threading.Thread(target=run_scheduler).start()


def loop(updater):
	print("[*] entering loop")
	updater.start_polling()
	updater.idle()

def main():
	init_time_data()
	updater    = init_telegram()
	
	dp = updater.dispatcher
	add_handlers_basic(dp)
	add_handlers_time(dp)
	add_homework_handler(dp)
	schedule_tasks(updater)

	loop(updater)

if __name__ == '__main__':
	main()