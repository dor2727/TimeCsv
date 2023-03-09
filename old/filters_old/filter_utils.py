import re
import operator
import functools

def _reduce_iterable(iterable, function):
	l = list(filter(bool, l))
	if not l:
		return None

	return functools.reduce(
		function,
		l
	)

def join_filters_with_or(l):
	return _reduce_iterable(l, operator.or_)

def join_filters_with_and(l: "Iterable[Filter]"):
	return _reduce_iterable(l, operator.and_)


def find_string_in_string(string_to_find, string_to_search_in, regex, case_sensitive):
	if       regex and     case_sensitive:
		return bool(re.findall(string_to_find, string_to_search_in))

	elif     regex and not case_sensitive:
		return bool(re.findall(string_to_find, string_to_search_in, re.I))

	elif not regex and     case_sensitive:
		return string_to_find in string_to_search_in

	elif not regex and not case_sensitive:
		return string_to_find in string_to_search_in.lower()

def find_string_in_list(string_to_find, list_to_search_in, regex, case_sensitive):
	if       regex and     case_sensitive:
		return any([
			re.findall(string_to_find, string_to_search_in)
			for string_to_search_in in list_to_search_in
		])

	elif     regex and not case_sensitive:
		return any([
			re.findall(string_to_find, string_to_search_in, re.I)
			for string_to_search_in in list_to_search_in
		])

	elif not regex and     case_sensitive:
		return string_to_find in list_to_search_in

	elif not regex and not case_sensitive:
		return string_to_find in map(str.lower, list_to_search_in)
