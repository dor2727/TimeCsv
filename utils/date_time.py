
def _get_ymd_tuple(d):
	"ymd stands for Year, Month, Day"
	return (d.year, d.month, d.day)

def are_dates_equal(d1, d2):
	return _get_ymd_tuple(d1) == _get_ymd_tuple(d2)
