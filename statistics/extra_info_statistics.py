from TimeCsv.statistics.base_statistics import DetailedStats
from TimeCsv.filters import GroupFilter, FriendFilter, LocationFilter

class DetailedStats_AllGroups(DetailedStats):
	def _get_titles(self):
		titles = set()

		for i in self.data:
			t = i.group
			if not t:
				print(f"empty group for: {i}")
			titles.add(t)

		# return a list, sorted alphabetically
		self._titles = sorted(titles)
		return self._titles

	def _get_items_of_title(self, title):
		return GroupFilter(title).get_filtered_data(self.data)

	# def _plot_make_clickable_pie(self, fig, patches):
	# 	def onclick(event):
	# 		patch = event.artist
	# 		label = patch.get_label()

	# 		print(f"=== {label} ===")

	# 		g = GroupGroupedStats(
	# 			self.data,
	# 			category_name=label.capitalize(),

	# 			selected_time=f"{self.selected_time} - {label}",

	# 			group_value=self.group_value,
	# 			sort=self._sorting_method,
	# 		)
	# 		print(g.to_text())
	# 		g.to_pie(save=False)

	# 	for patch in patches:
	# 		patch.set_picker(True)

	# 	fig.canvas.mpl_connect('pick_event', onclick)

	# def to_pie(self, headers=None, values=None, title=None, save=True):
	# 	"""
	# 	if bool(save) is False: interactively show the pie chard
	# 	if save is str: save the image to that path
	# 	if save is True: save to the default location

	# 	if save:
	# 		return open handle to the file with the image
	# 	"""
	# 	headers, values = self._plot_prepare_data(headers, values)

	# 	# plotting initialization
	# 	fig, ax = plt.subplots()

	# 	patches = self._plot_make_pie(ax, values, headers)

	# 	self._plot_set_title(fig, ax, title)

	# 	self._plot_make_clickable_pie(fig, patches)

	# 	return self._plot_save(fig, save)

class DetailedStats_Friend(DetailedStats):
	def _get_titles(self):
		titles = set()

		for i in self.data:
			if i.friends:
				titles.update(i.friends)

		# return a list, sorted alphabetically
		self._titles = sorted(titles)
		return self._titles

	def _get_items_of_title(self, title):
		return FriendFilter(title).get_filtered_data(self.data)

class DetailedStats_Location(DetailedStats):
	def _get_titles(self):
		titles = set()

		for i in self.data:
			titles.add(i.location)

		if None in titles:
			titles.remove(None)

		# return a list, sorted alphabetically
		self._titles = sorted(titles)
		return self._titles

	def _get_items_of_title(self, title):
		return LocationFilter(title).get_filtered_data(self.data)
