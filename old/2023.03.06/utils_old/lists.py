from collections import OrderedDict, Counter

def ordered_unique(l):
	return list(OrderedDict.fromkeys(l))

def counter(data):
    return list(Counter(data).items())
