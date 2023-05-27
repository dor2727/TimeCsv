from pandas import DataFrame
from ..utils.times import seconds_to_time_str, Seconds, Days

class Statistics:
	def __init__(self, df: DataFrame):
		self.df = df

	@property
	def num_events(self) -> int:
		return self.df.shape[0]

	@property
	def total_seconds(self) -> Seconds:
		return self.df.total_seconds.sum()

	@property
	def total_seconds_str(self) -> str:
		return seconds_to_time_str(self.total_seconds)

	def percentage_of_seconds(self, total_seconds: Seconds) -> float:
		return 100.0 * self.total_seconds / total_seconds

	def percentage_of_seconds_str(self, total_seconds: Seconds) -> str:
		return seconds_to_time_str(self.percentage_of_seconds(total_seconds))

	@property
	def average_time_of_event(self):
		if self.num_events == 0:
			return 0

		return self.total_seconds / self.num_events

	def _total_duration(self, start_date=None, stop_date=None) -> Days:
		if start_date is None:
			start_date = self.df.date.min()
		if stop_date is None:
			stop_date = self.df.date.max()

		return stop_date - start_date

	def amount_of_days(self, start_date=None, stop_date=None) -> Days:
		return self._total_duration(start_date, stop_date).days
	def amount_of_days_in_seconds(self, start_date=None, stop_date=None) -> Seconds:
		return self._total_duration(start_date, stop_date).days


	def average_time_between_events(self, start_date=None, stop_date=None) -> Seconds:
		# return in seconds
		if self.num_events == 0:
			return 0
		if self.num_events == 1:
			return 0

		return self.amount_of_days_in_seconds(start_date, stop_date) / self.num_events

	def average_time_between_events_str(self, start_date=None, stop_date=None) -> str:
		return seconds_to_time_str(self.average_time_between_events(start_date, stop_date))
