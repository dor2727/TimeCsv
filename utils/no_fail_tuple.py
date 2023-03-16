class no_fail_tuple(tuple):
	def __getitem__(self, index):
		try:
			return super().__getitem__(index)
		except KeyError:
			return None
