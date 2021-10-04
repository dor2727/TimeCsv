import re

from TimeCsv.filters.base_filters import Filter

class DescriptionFilter(Filter):
	def __init__(self, string, case_sensitive=None, regex=False):
		self.case_sensitive = case_sensitive or False
		self.regex = regex

		if self.case_sensitive:
			self.string = string
		else:
			self.string = string.lower()

	def filter(self, data):
		if       self.regex and     self.case_sensitive:
			return [
				bool(re.findall(self.string, i.description))
				for i in data
			]

		elif     self.regex and not self.case_sensitive:
			return [
				bool(re.findall(self.string, i.description, re.I))
				for i in data
			]

		elif not self.regex and     self.case_sensitive:
			return [
				self.string in i.description
				for i in data
			]

		elif not self.regex and not self.case_sensitive:
			return [
				self.string in i.description.lower()
				for i in data
			]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.string})"

class GroupFilter(Filter):
	def __init__(self, string, case_sensitive=None, regex=False):
		self.case_sensitive = case_sensitive or True
		self.regex = regex

		if self.case_sensitive:
			self.string = string
		else:
			self.string = string.lower()

	def filter(self, data):
		if       self.regex and     self.case_sensitive:
			return [
				bool(re.findall(self.string, i.group))
				for i in data
			]

		elif     self.regex and not self.case_sensitive:
			return [
				bool(re.findall(self.string, i.group, re.I))
				for i in data
			]

		elif not self.regex and     self.case_sensitive:
			return [
				self.string in i.group
				for i in data
			]

		elif not self.regex and not self.case_sensitive:
			return [
				self.string in i.group.lower()
				for i in data
			]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.string})"

class FriendFilter(Filter):
	def __init__(self, friend, case_sensitive=False):
		self.case_sensitive = case_sensitive

		if self.case_sensitive:
			self.friend = friend
		else:
			self.friend = friend.lower()

	def filter(self, data):
		if self.case_sensitive:
			return [
				self.friend in i.friends
				for i in data
			]

		else: # not case_sensitive
			return [
				self.friend in map(str.lower, i.friends)
				for i in data
			]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.friend})"

class LocationFilter(Filter):
	def __init__(self, location, case_sensitive=False):
		self.case_sensitive = case_sensitive

		if self.case_sensitive:
			self.location = location
		else:
			self.location = location.lower()

	def filter(self, data):
		if self.case_sensitive:
			return [
				self.location == i.location
				for i in data
			]

		else: # not case_sensitive
			return [
				self.location in i.location.lower()
				for i in data
				if i.location
			]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.location})"

class HasExtraDetailsFilter(Filter):
	def filter(self, data):
		return [
			bool(i.extra_details)
			for i in data
		]

class DurationFilter(Filter):
	def __init__(self, string):
		if   type(string) is str and string[0] == '<':
			self._action = "maximum"
			self.seconds = self._int(string[1:])
		elif type(string) is str and string[0] == '>':
			self._action = "minumum"
			self.seconds = self._int(string[1:])
		else: # default
			self._action = "maximum"
			self.seconds = self._int(string)

	def _int(self, string):
		# the input may be 100.0
		return int(string.split('.')[0])

	def filter(self, data):
		if self._action == "maximum":
			return [
				int(i) <= self.seconds
				for i in data
			]
		elif self._action == "minumum":
			return [
				int(i) >= self.seconds
				for i in data
			]
		else:
			raise ValueError("Invalid action")

	def __repr__(self):
		return f"{self.__class__.__name__}({self._action} {self.seconds} seconds)"

