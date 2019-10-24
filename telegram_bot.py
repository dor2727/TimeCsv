#!/usr/local/bin/python3.7

import threading
import time
import schedule
import Time.statistics
from telegram.ext import Updater, InlineQueryHandler, CommandHandler

from pdb import set_trace

MY_CHAT_ID = int(open('chat_id').read().strip())

# handlers
def test(message, update):
	print("[*] got command - test")
	chat_id = message['message']['chat']['id']
	update.bot.sendMessage(chat_id, "test")

def pdb(message, update):
	print("[*] got command - pdb")
	set_trace()

def start(message, update):
	global MY_CHAT_ID
	MY_CHAT_ID = message['message']['chat']['id']
	print(f"[*] start - {MY_CHAT_ID}")
	
# initialization funcitons
def init_time_data():
	print("[*] initializing time data")
	my_time_data = Time.statistics.TimeParser(path="/home/me/Dropbox/Projects/Time/data/big_holiday_2019.tcsv")
	my_bot_api   = Time.statistics.TelegramBotAPI(my_time_data.get_data)
	return my_bot_api

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

def add_handlers_time(dp, my_bot_api):
	print("[*] adding handlers - time")
	for i in ("last_day", "last_week", "current_week", "today"):
		dp.add_handler(CommandHandler(
			i,
			my_bot_api.create_bot_command(i)
		))
		dp.add_handler(CommandHandler(
			i + "_full",
			my_bot_api.create_bot_command(i, full_report=True)
		))


# schedualing functions
def send_message(updater, text):
	updater.bot.sendMessage(MY_CHAT_ID, text)
def send_report(updater, my_bot_api, report_name):
	report_data = my_bot_api.create_report(report_name)
	report_text = '\n'.join(report_data)
	send_message(updater, report_text)

def schedule_tasks(updater, my_bot_api):
	daily  = lambda : send_report(updater, my_bot_api, "last_day")
	schedule.every().day.at("08:00").do(daily)
	

	weekly = lambda : send_report(updater, my_bot_api, "last_week")
	schedule.every().sunday.at("08:00").do(weekly)

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
	my_bot_api = init_time_data()
	updater    = init_telegram()
	
	dp = updater.dispatcher
	add_handlers_basic(dp)
	add_handlers_time(dp, my_bot_api)
	schedule_tasks(updater, my_bot_api)

	loop(updater)

if __name__ == '__main__':
	main()