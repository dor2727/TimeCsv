import enum

class SortingMethods(enum.Enum):
	Alphabetically = "alphabetically"
	TotalTime = "total_time"
	NumEvents = "num_events"

	def __str__(self):
		return self.value

class Outputs(enum.Enum):
	Terminal = "terminal"
	Pie = "pie"
