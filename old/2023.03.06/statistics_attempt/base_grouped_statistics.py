
def _validate_method(value, allowed_values):
	value = value.lower()

	if value not in allowed_values:
		raise ValueError(f"invalid method: {value}. The allowed values are: {allowed_values}")

	return value

class DataGroupedStatistics(DataHolder):
	_allowed_sorting_methods  = ("alphabetically", "by_value")
	_allowed_statistics_methods = ("total_time", "average_time", "amount_of_events")

	def __init__(self, data, statistics_method="total_time", sorting_method="by_value", **kwargs):
		super().__init__(data, **kwargs)

		self._statistics_method = _validate_method(
			statistics_method,
			self._allowed_statistics_methods
		)
		self._sorting_method = _validate_method(
			sorting_method,
			self._allowed_sorting_methods
		)

class DataFlattenGroupedStatistics(DataGroupedStatistics):
	pass
class DataRecursiveGroupedStatistics(DataGroupedStatistics):
	pass
