#!/usr/bin/env python3
import numpy as np

from TimeCsv import DataFolder, DescriptionFilter, GroupFilter

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
	data = shave_filter % datafolder.data

	diff = get_beard_growing_amount(data)
	# from seconds to days
	diff /= 60*60*24

	print(f"Shaving every {diff.mean():.2f} ± {diff.std():.2f} days")
	print(f"average shave time: {np.mean(data) / 60:.2f} minutes")

if __name__ == '__main__':
	get_shave_statistics()
