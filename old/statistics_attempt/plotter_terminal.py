from TimeCsv.statistics.base_statistics import DataPlotter

INDENTATION = "  "

class DataPlotterTerminal(DataPlotter):
	def _create_header(self) -> str:
		s  = self.time_representation_str
		s += "\n"
		s += f"{INDENTATION}events per day = {self.events_per_day:.2f}"
		s += "\n"

		return s

	def to_text(self):
		s = self._create_header()

		s += "%s(%3d) : %s (%5.2f%%) │ item average %s │ distance average %s" % (
			INDENTATION * 2,
			self.amount_of_items,
			seconds_to_str(self.amount_of_time),
			self.time_percentage,
			seconds_to_str(self.amount_of_time_on_average),
			seconds_to_str(self.time_between_events_on_average),
		)

		return s

	def to_telegram(self):
		s = self._create_header()

		s += "%s(%3d) : %s (%5.2f%%)" % (
			INDENTATION * 2,
			self.amount_of_items,
			seconds_to_str(self.amount_of_time),
			self.time_percentage,
		)
		s += "%sitem average %s" % (
			INDENTATION * 4,
			seconds_to_str(self.amount_of_time_on_average),
		)
		s += "%sdistance average %s" % (
			INDENTATION * 4,
			seconds_to_str(self.time_between_events_on_average),
		)

		return s
