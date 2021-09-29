import TimeCsv.statistics
from TimeCsv.parsing import DataFolder
from TimeCsv.filters import *
import numpy as np

shave_filter = DescriptionFilter("shave") & GroupFilter("Life")

def get_beard_growing_amount(data):
	diff = []
	for i in range(len(data)-1):
		diff_time = data[i+1].start_time - data[i].start_time

		# ignore shaving that was split in the same day, or in consecutive days
		if diff_time.days <= 2:
			continue

		# ignore long beard-growing times
		if diff_time.days >= 30:
			continue

		diff_time_in_seconds = diff_time.total_seconds()
		diff.append(diff_time_in_seconds)

	diff = np.array(diff)
	return diff

def get_shave_statistics(datafolder=None):
	datafolder = datafolder or DataFolder()
	d = shave_filter % datafolder.data

	diff = get_beard_growing_amount(d)
	# from seconds to days
	diff /= 60*60*24

	# print(diff)
	print(f"Shaving every {diff.mean():.2f} ± {diff.std():.2f} days")
	print(f"average shave time: {np.mean(d) / 60:.2f} minutes")
