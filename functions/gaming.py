#!/usr/bin/env python3
from TimeCsv import DataFolder, ExtraDetailsFilter, GroupFilter

# It is "Gamin" in purpose - to remind that it catches all "Gaming*"
lol_filter = ExtraDetailsFilter("lol") & GroupFilter("Gamin") & ~GroupFilter("GamingWatch")

def get_lol_statistics(datafolder=None):
	datafolder = datafolder or DataFolder()
	data = lol_filter % datafolder.data

	lol_games = 0
	lol_games_solo = 0
	lol_games_social = 0
	max_games_in_one_session = 0
	# Using a for-loop for validation
	for i in data:
		assert "lol" in i.extra_details
		assert len(i.extra_details) == 1
		assert len(i.extra_details["lol"]) == 1
		assert i.extra_details["lol"][0].isdigit()
		amount_of_games = int(i.extra_details["lol"][0])

		lol_games += amount_of_games
		if "Solo" in i.group:
			lol_games_solo += amount_of_games
		if "Social" in i.group:
			lol_games_social += amount_of_games

		if amount_of_games > max_games_in_one_session:
			max_games_in_one_session = amount_of_games

	print(f"Total lol games       : {lol_games}")
	print(f"Total lol games solo  : {lol_games_solo}")
	print(f"Total lol games social: {lol_games_social}")
	print(f"{max_games_in_one_session=}")

if __name__ == '__main__':
	get_lol_statistics()
