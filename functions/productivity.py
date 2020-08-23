import matplotlib.pyplot as plt

from TimeCsv.parsing import DataFolder
from TimeCsv.filters import *

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

def get_productivity_pie(data=None, selected_time="All time", save=True, focused=False):
	data = data or DataFolder().data

	productivity_groups = PRODUCTIVITY_FOCUSED_GROUPS if focused else PRODUCTIVITY_GROUPS

	headers = [i["name"] for i in productivity_groups]
	filtered_data = [
		i["filter"] % data
		for i in productivity_groups
	]
	# sum over the DataItem list, resulting in the total amount of seconds
	values = list(map(sum, filtered_data))
	total_seconds = sum(values)


	# plotting

	# plotting initialization
	fig, ax = plt.subplots()

	# text inside the pie chart
	def pct(value):
		# value is given as a percentage - a float between 0 to 100
		return f"{value:.1f}%"

	# making the pie chart
	patches, _, _ = ax.pie(values, labels=headers, autopct=pct)

	# Equal aspect ratio ensures that pie is drawn as a circle.
	ax.axis('equal')

	# labels
	labels = [f"{seconds_to_hours_str(i)} h" for i in values]
	plt.legend(patches, labels, loc="upper left")
	# titles
	ax.set_title(f"Productive Pie - {selected_time}")
	fig.canvas.set_window_title(f"Productive Pie - {selected_time}")

	# plotting - save to file
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
		fig.show()
		import pdb; pdb.set_trace()
		return None

