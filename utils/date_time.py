import datetime

def get_ymd_tuple(d):
	"ymd stands for Year, Month, Day"
	return (d.year, d.month, d.day)

def get_midnight(d):
	return datetime.datetime(*get_ymd_tuple(d))

def seconds_to_str(n):
	n = int(n)

	s = ''

	days = (n // (60*60*24))
	if days:
		s += f"{days:3d} days"
	else:
		s += " " * (3+1+4)

	s += ' '

	hours = (n // (60*60) % (24))
	if hours:
		s += f"{hours:2d} hours"
	else:
		s += " " * (2+1+5)

	s += ' '

	minutes = (n // (60) % (60*24) % 60)
	if minutes:
		s += f"{minutes:2d} minutes"
	else:
		s += " " * (2+1+7)

	return s

def seconds_to_hours_str(n):
	h = n / (3600)
	return f"{h:.2f}"

def shorten_selected_time(selected_time):
	if len(selected_time) > 33:
		return "Multiple Time Filters"
	else:
		return selected_time

def format_dates(date1, date2):
	return DATE_REPRESENTATION_PATTERN % (
		*get_ymd_tuple(date1),
		*get_ymd_tuple(date2),
	)
