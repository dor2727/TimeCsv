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
