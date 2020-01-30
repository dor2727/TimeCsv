import datetime
import re
import matplotlib.pyplot as plt

WEEK_STARTS_AT_SUNDAY = True

def seconds_to_str(n):
	return ("%2d days %2d hours %2d minutes" % (
		n // (60*60*24),
		n // (60*60) % (24),
		n // (60) % (60*24) % 60,
	)).replace(" 0 days", "       ").replace(" 0 hours", "        ")


def get_ymd_tuple(d):
	"ymd stands for Year, Month, Day"
	return (d.year, d.month, d.day)

def get_midnight(d):
	return datetime.datetime(*get_ymd_tuple(d))




class TelegramBotAPI_TimedCommands(object):
	def _create_report__last_day(self):
		yesterday = get_midnight(datetime.datetime.now() - datetime.timedelta(days=1))
		today = yesterday + datetime.timedelta(days=1)

		self.data = self.get_data(date_range=( yesterday, today ))
	def _create_report__today(self):
		now = datetime.datetime.now()
		today = get_midnight(now)

		self.data = self.get_data(date_range=( today, now ))
	def _create_report__last_week(self):
		today = datetime.datetime.now()

		if WEEK_STARTS_AT_SUNDAY:
			weekday = today.weekday() + WEEK_STARTS_AT_SUNDAY
			if weekday == 7:
				weekday = 0
		else:
			weekday = today.weekday()
		this_sunday = get_midnight(today - datetime.timedelta(days=weekday))
		prev_sunday = this_sunday - datetime.timedelta(days=7)

		self.data = self.get_data(date_range=( prev_sunday, this_sunday ))
	def _create_report__current_week(self):
		end_date = datetime.datetime.now()

		if WEEK_STARTS_AT_SUNDAY:
			weekday = end_date.weekday() + WEEK_STARTS_AT_SUNDAY
			if weekday == 7:
				weekday = 0
		else:
			weekday = end_date.weekday()
		start_date = get_midnight(end_date - datetime.timedelta(days=weekday))

		self.data = self.get_data(date_range=( start_date, end_date ))


DEFAULT_REPORTERS = [
	"Gaming",
	"Read",
	"Life",
	"homework",
]
FULL_REPORTERS = [
	"Gaming",
	"Read",
	"Life",
	"homework",
	"physics lab",
	"lol",
]

class TelegramBotAPI_Getters(object):
	def _find_items_by_group(self, s):
		filter_func = lambda x: x.group == s
		return list(filter(filter_func, self.items))
	def _find_items_in_description(self, s):
		filter_func = lambda x: s in x.description
		return list(filter(filter_func, self.items))

	def _default_getter(self, name):
		def f():
			if name[0].isupper():
				items = self._find_items_by_group(name)
			else:
				items = self._find_items_in_description(name)

			return (
				len(items),
				sum(int(i) for i in items),
			)
		return f


	def _format_getter_raw(self, name, n_items, n_seconds):
		try:
			seconds_percentage = n_seconds / self._all_time_total * 100
		except Exception as e:
			seconds_percentage = 0

		try:
			avg_per_item       = n_seconds / n_items if n_items else 0
		except Exception as e:
			avg_per_item = 0

		return f"{name} : {n_items} : {seconds_to_str(n_seconds)} ({seconds_percentage:.2f}%)"
		# return f"{name:20s} : {n_items:3d} : {seconds_to_str(n_seconds)} ({seconds_percentage:.2f}%)"
		# return f"{name:20s} : {n_items:3d} : {seconds_to_str(n_seconds)} ({seconds_percentage:.2f}%) ; item average {seconds_to_str(avg_per_item)}"


	def _format_getter(self, name):
		n_items, n_seconds = getattr(
			self,
			"_getter__" + name,
			self._default_getter(name)
		)()

		return self._format_getter_raw(name, n_items, n_seconds)
		
class TelegramBotAPI_Getters_Homework(object):
	def _create_pie(self, x, labels, title):
		fig, ax = plt.subplots()

		ax.set_title(title)
		ax.pie(x, labels=labels)
		ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
		fig.savefig(f"/tmp/pie.png")
		plt.close(fig)

		return open(f"/tmp/pie.png", "rb")

	def _create_homework_pie(self, homework, amount=False):
		homework_types = sorted(list(homework.keys()))

		data_amount = [homework[t]["amount"] for t in homework_types]
		data_time = [homework[t]["time"] for t in homework_types]

		total_time = sum(data_time) or 1 # to avoid division by zero
		for t in homework_types:
			homework[t]["percentage"] = 100 * homework[t]["time"] / total_time

		title = seconds_to_str(total_time)
		labels = [f"{t} ({homework[t]['percentage']:.0f}%)" for t in homework_types]

		if amount:
			return self._create_pie(data_amount, labels, title)
		else:
			return self._create_pie(data_time,   labels, title)

	def _create_homework_text(self, homework, amount=False):
		labels = sorted(list(homework.keys()))
		# move "other" to last place
		if "other" in labels:
			labels.remove("other")
			labels.append("other")

		return '\n'.join(
			self._format_getter_raw(name, homework[name]["amount"], homework[name]["time"])
			for name in labels
		)

	def _homework_getter(self):
		all_homework = self._find_items_in_description("homework")
		homework_types = list(set(
			re.findall(
				"\\((.*?)\\)",
				'\n'.join(i.description for i in all_homework)
			)
		))

		homework = {}

		for t in homework_types:
			homework[t] = {}
			homework[t]["items"] = [i for i in all_homework if t in i.description]
			homework[t]["amount"] = len(homework[t]["items"])
			homework[t]["time"] = sum(int(i) for i in homework[t]["items"])

		homework["other"] = {}
		homework["other"]["items"] = [i for i in all_homework if not any ([t in i.description for t in homework_types])]
		homework["other"]["amount"] = len(homework["other"]["items"])
		homework["other"]["time"] = sum(int(i) for i in homework["other"]["items"])

		return homework

		labels = sorted(homework_types) + ["other"]
		data_amount = [homework[l]["amount"] for l in labels]
		data_time = [homework[l]["time"] for l in labels]

		total_time = sum(int(i) for i in all_homework)
		title = seconds_to_str(total_time)

		pie_amount = self._create_pie(data_amount, labels, title, 1)
		pie_time   = self._create_pie(data_time,   labels, title, 2)
		return pie_time, pie_amount



class TelegramBotAPI(TelegramBotAPI_TimedCommands, TelegramBotAPI_Getters, TelegramBotAPI_Getters_Homework):
	def __init__(self, get_data, reporters=None):
		self.get_data = get_data
		self.reporters = reporters or DEFAULT_REPORTERS

	def _init_getter_format(self):
		self._all_time_total = sum(int(i) for i in self.items)

	def create_report(self, report_name, reporters=None):
		reporters = reporters or self.reporters

		# create self.data
		getattr(self, "_create_report__" + report_name)()
		self.items = self.data[0]
		self._init_getter_format()

		reporters_str = []
		for r in reporters:
			reporters_str.append(self._format_getter(r))

		return reporters_str

	def create_bot_command(self, name, full_report=False):
		def f(message, update):
			print(f"[*] got command - {name} [full={full_report}]")
			chat_id = message['message']['chat']['id']

			reporters = FULL_REPORTERS if full_report else None
			report_data = self.create_report(name, reporters=reporters)
			text = self.data[1] + '\n' + '\n'.join(report_data)
			update.bot.sendMessage(chat_id, text)
		return f

	def create_homework_pie_command(self, amount=False, report_name="current_week"):
		"""
		if amount is true: return a pie chart with amount of instances
		else, return pie with total time
		"""

		def f(message, update):
			print(f"[*] got command - homework pie [amount={amount}]")
			chat_id = message['message']['chat']['id']

			# create self.data
			getattr(self, "_create_report__" + report_name)()
			self.items = self.data[0]
			self._init_getter_format()

			homework = self._homework_getter()
			image_file = self._create_homework_pie(homework, amount=amount)
			update.bot.send_photo(chat_id, photo=image_file)
		return f
	def create_homework_text_command(self, amount=False, report_name="current_week"):
		"""
		if amount is true: return a pie chart with amount of instances
		else, return pie with total time
		"""

		def f(message, update):
			print(f"[*] got command - homework text [amount={amount}]")
			chat_id = message['message']['chat']['id']

			# create self.data
			getattr(self, "_create_report__" + report_name)()
			self.items = self.data[0]
			self._init_getter_format()

			homework = self._homework_getter()
			text = self._create_homework_text(homework, amount=amount)
			update.bot.sendMessage(chat_id, text)
		return f
