import matplotlib.pyplot as plt

from TimeCsv.parsing import DataFolder
from TimeCsv.filters import *
import TimeCsv.statistics

PRODUCTIVITY_GROUPS = [
	{
		"name": "Life",
		"index": 1,
		"filter": (
			(GroupFilter("Life") & ~DescriptionFilter("toilet"))
			 |
			GroupFilter("Ill")
		),
	},
	{
		"name": "Chen",
		"index": 2,
		"filter": GroupFilter("Chen"),
	},
	{
		"name": "Social",
		"index": 3,
		"filter": (
			(GroupFilter("Friends") & ~DescriptionFilter("whatsapp"))
			 |
			GroupFilter("Family")
		)
	},
	{
		"name": "Job",
		"index": 4,
		"filter": (
			GroupFilter("University")
			 |
			GroupFilter("Project")
			 |
			GroupFilter("Work")
		),
	},
	{
		"name": "Productive",
		"index": 5,
		"filter": (
			# Creating content
			GroupFilter("Blog")
			 |
			GroupFilter("Book")
			 |
			# another type of content
			GroupFilter("Programming")
			 |

			# Consuming content
			GroupFilter("Read")
			 |
			GroupFilter("Study")
			 |
			GroupFilter("Podcast")
			 |
			GroupFilter("Ted")
			 |
			(GroupFilter("Reddit") &  DescriptionFilter("weekly update"))
			 |

			# self management
			GroupFilter("Time")
			 |
			GroupFilter("Think")
			 |
			GroupFilter("Meditate")
			# I'll add Sport to self management
			 |
			GroupFilter("Sport")
		),
	},
	{
		"name": "Junk",
		"index": 6,
		"filter": (
			GroupFilter("Gaming")
			 |
			GroupFilter("Youtube")
			 |
			(GroupFilter("Reddit") & ~DescriptionFilter("weekly update"))
			 |
			(GroupFilter("Friends") &  DescriptionFilter("whatsapp"))
		),
	},
	{
		"name": "Other",
		"index": 7,
		"filter": (
			GroupFilter("Computer")
			 |
			GroupFilter("Shopping")
			 |

			GroupFilter("Transportation")
			 |
			GroupFilter("Wait")
			 |
			GroupFilter("Chores")
			 |
			GroupFilter("Money")
			 |
			(GroupFilter("Life") &  DescriptionFilter("toilet"))
			 |

			GroupFilter("Chill")
			 |
			GroupFilter("Vacation")
			 |
			GroupFilter("Morning")
			 |
			GroupFilter("Other")
		),
	},
]

PRODUCTIVITY_FOCUSED_GROUPS = [
	{
		"name": "Consuming Content",
		"index": 1,
		"filter": (
			GroupFilter("Read")
			 |
			GroupFilter("Study")
			 |
			GroupFilter("Podcast")
			 |
			GroupFilter("Ted")
			 |
			(GroupFilter("Reddit") &  DescriptionFilter("weekly update"))
		),
	},
	{
		"name": "Creating Content",
		"index": 2,
		"filter": (
			GroupFilter("Blog")
			 |
			GroupFilter("Book")
			 |
			GroupFilter("Programming")
		),
	},
	{
		"name": "Self Management",
		"index": 3,
		"filter": (
			GroupFilter("Time")
			 |
			GroupFilter("Think")
			 |
			GroupFilter("Meditate")
			 |
			GroupFilter("Sport")
		),
	},
	{
		"name": "Consuming Junk",
		"index": 4,
		"filter": (
			GroupFilter("Youtube")
			 |
			(GroupFilter("Reddit") & ~DescriptionFilter("weekly update"))
		)
	},
	{
		"name": "Gaming",
		"index": 5,
		"filter": (
			GroupFilter("Gaming")
		),
	},
	
	{
		"name": "Other - available",
		"index": 6,
		"filter": (
			GroupFilter("Transportation")
		),
	},
	{
		"name": "Other - truncatble",
		"index": 7,
		"filter": (
			GroupFilter("Wait")
			 |
			(GroupFilter("Life") &  DescriptionFilter("toilet"))
			 |
			GroupFilter("Chill")
			 |
			GroupFilter("Morning")
			 |
			GroupFilter("Other")
			 |
			(GroupFilter("Friends") &  DescriptionFilter("whatsapp"))
		),
	},
]

def prepare_data(data=None, focused=False):
	data = data or DataFolder().data

	productivity_groups = PRODUCTIVITY_FOCUSED_GROUPS if focused else PRODUCTIVITY_GROUPS

	headers = [i["name"] for i in productivity_groups]
	filtered_data = [
		i["filter"] % data
		for i in productivity_groups
	]
	# sum over the DataItem list, resulting in the total amount of seconds
	values = list(map(sum, filtered_data))

	return headers, values, data, productivity_groups

def make_pie(ax, headers, values):
	# text inside the pie chart
	def pct(value):
		# value is given as a percentage - a float between 0 to 100
		return f"{value:.1f}%"

	# making the pie chart
	patches, _, _ = ax.pie(values, labels=headers, autopct=pct)

	# Equal aspect ratio ensures that pie is drawn as a circle.
	ax.axis('equal')

	return patches

def save_pie(fig, save):
	if save:
		if save is True:
			path = DEFAULT_PIE_PATH
		else:
			path = save

		fig.savefig(path)
		plt.close(fig)

		return open(path, "rb")
	# plotting - interactive
	else:
		plt.show()
		return None


def make_clickable_pie(fig, patches, data, productivity_groups, title):
	def onclick(event):
		patch = event.artist
		label = patch.get_label()

		group = [i for i in productivity_groups if i["name"] == label][0]

		filtered_data = group["filter"] % data

		print(f"=== {label} ===")

		g = TimeCsv.statistics.GroupedStats_Group(filtered_data, selected_time=f"{title} - {label}")
		print(g.to_text())
		g.to_pie(save=False)

	for patch in patches:
		patch.set_picker(True)

	fig.canvas.mpl_connect('pick_event', onclick)


def get_productivity_pie(data=None, selected_time="All time", save=True, focused=False):
	headers, values, data, productivity_groups = prepare_data(data, focused)

	# plotting initialization
	fig, ax = plt.subplots()

	patches = make_pie(ax, headers, values)


	# labels
	labels = [f"{h} - {seconds_to_hours_str(v)} h" for h, v in zip(headers, values)]
	plt.legend(patches, labels, loc="upper left")

	# titles
	title = f"Productive Pie - {selected_time}"
	ax.set_title(title)
	fig.canvas.set_window_title(f"Productive Pie - {selected_time}")


	make_clickable_pie(fig, patches, data, productivity_groups, title)

	return save_pie(fig, save)

if __name__ == '__main__':
	get_productivity_pie()
