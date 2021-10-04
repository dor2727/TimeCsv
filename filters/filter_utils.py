import operator
import functools

def join_filters_with_or(l):
	# check if list is empty
	l = list(filter(bool, l))
	if not l:
		return None

	return functools.reduce(
		operator.or_,
		l
	)

def join_filters_with_and(l):
	# check if list is empty
	l = list(filter(bool, l))
	if not l:
		return None

	return functools.reduce(
		operator.and_,
		l
	)

# todo: look at this
def get_named_filter(name, args=None):
	if name == "today":
		if args is None:
			return TimeFilter_Days(1)
		# todo: why is this here?
		elif type(args) is int:
			return TimeFilter_Days(args)
		else:
			return TimeFilter_Days(*args)

	elif name == "yesterday":
		stop_time  = get_midnight( datetime.datetime.now() )
		start_time = get_midnight(
			stop_time
			 -
			datetime.timedelta(days=1)
		)

		return TimeFilter_DateRange( start_time, stop_time )

	elif name == "week":
		return TimeFilter_Days(7)

	elif name == "last_week":
		today = datetime.datetime.now()

		if WEEK_STARTS_AT_SUNDAY:
			weekday = today.weekday() + WEEK_STARTS_AT_SUNDAY
			if weekday == 7:
				weekday = 0
		else:
			weekday = today.weekday()
		this_sunday = get_midnight(today - datetime.timedelta(days=weekday))
		prev_sunday = this_sunday - datetime.timedelta(days=7)

		return TimeFilter_DateRange( prev_sunday, this_sunday )

	elif name == "month":
		if args is None:
			return TimeFilter_Month()
		elif type(args) is int:
			return TimeFilter_Month(args)
		else:
			return TimeFilter_Month(*args)

	elif name == "year":
		if args is None:
			return TimeFilter_Year()
		elif type(args) is int:
			return TimeFilter_Year(args)
		else:
			return TimeFilter_Year(*args)

	elif name == "all":
		return TrueFilter()

	else:
		return None
