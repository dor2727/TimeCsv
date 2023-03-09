Seconds = int
Minutes = int
Hours = int
Days = int

def seconds_to_time_str(seconds: int):
	s = ''

	days = (seconds // (60*60*24))
	if days:
		s += f"{days:3d} d"
	else:
		s += " " * (3+1+1)

	s += ' '

	hours = (seconds // (60*60) % (24))
	minutes = (seconds // (60) % (60*24) % 60)
	s += f"{hours:02d}:{minutes:02d}"

	return s
