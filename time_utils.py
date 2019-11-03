import datetime

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



DEFAULT_REPORTERS = [
	"afk arena",
	"call of duty mobile",
	"lol",
]
FULL_REPORTERS = [
	"Gaming",
	"afk arena",
	"idle heroes",
	"call of duty mobile",
	"maplestory mobile",
	"lol",
	"Read",
	"Life",
	"Chores",
	"Family",
]

class TelegramBotAPI(object):
	def __init__(self, get_data, reporters=None):
		self.get_data = get_data
		self.reporters = reporters or DEFAULT_REPORTERS

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

	def _init_getter_format(self):
		self._all_time_total = sum(int(i) for i in self.items)

	def create_report(self, time, reporters=None):
		reporters = reporters or self.reporters
		# create self.data
		getattr(self, "_create_report__" + time)()
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

	#
	def _find_items_by_group(self, s):
		filter_func = lambda x: x.group == s
		return list(filter(filter_func, self.items))
	def _find_items_in_description(self, s):
		filter_func = lambda x: s in x.description
		return list(filter(filter_func, self.items))
	def _description_getter(self, name):
		def f():
			items = self._find_items_in_description(name)
			return (
				len(items),
				sum(int(i) for i in items),
			)
		return f

	def _format_getter(self, name):
		n_items, n_seconds = getattr(
			self,
			"_getter__" + name,
			self._description_getter(name)
		)()

		try:
			seconds_percentage = n_seconds / self._all_time_total * 100
		except Exception as e:
			seconds_percentage = 0

		try:
			avg_per_item       = n_seconds / n_items if n_items else 0
		except Exception as e:
			avg_per_item = 0

		return f"{name:20s} : {n_items:3d} : {seconds_to_str(n_seconds)} ({seconds_percentage:.2f}%) ; item average {seconds_to_str(avg_per_item)}"

	def _getter__Gaming(self):
		items = self._find_items_by_group("Gaming")
		return (
			len(items),
			sum(int(i) for i in items),
		)
	def _getter__Read(self):
		items = self._find_items_by_group("Read")
		return (
			len(items),
			sum(int(i) for i in items),
		)
	def _getter__Life(self):
		items = self._find_items_by_group("Life")
		return (
			len(items),
			sum(int(i) for i in items),
		)
	def _getter__Chores(self):
		items = self._find_items_by_group("Chores")
		return (
			len(items),
			sum(int(i) for i in items),
		)
	def _getter__Family(self):
		items = self._find_items_by_group("Family")
		return (
			len(items),
			sum(int(i) for i in items),
		)
	