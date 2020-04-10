
""" testing filters

	# f = AutoFilter("Read").get_filtered_data(b.data)
	# f = AutoTimeFilter(2).get_filtered_data(b.data)

	# f = AutoFilter("lecture\\b").get_filtered_data(b.data)
	# f = AutoFilter("lol").get_filtered_data(b.data)
	# f = AutoFilter("power").get_filtered_data(b.data)
	# f = AutoFilter("ups").get_filtered_data(b.data)
	# f = AutoFilter("prepare").get_filtered_data(b.data)
	f = AutoFilter("piece").get_filtered_data(b.data)
	print(len(f))
	print('\n'.join(map(str,f)))
"""

""" testing time filters & filter chains

	f1 = AutoFilter("ups")
	f2 = TimeFilter_Days(7)
	f3 = TimeFilter_Year()
	f = f1 & (f2 | f3)
	f_data = f.get_filtered_data(b.data)
	f_time = f.selected_time
	print(f_time)
	print(len(f_data))
	print('\n'.join(map(str,f_data)))
	print("----------")
	s = TimeCsv.statistics.FilteredStats(f_data, f_time)
	print(s.to_text())
	print("----------")
"""

""" testing GroupedStats

	# f = AutoFilter("ping pong").get_filtered_data(b.data)
	f = AutoFilter("ping pong") % b.data
	print(len(f))
	print('\n'.join(map(str,f)))
	print("----------")
	g = TimeCsv.statistics.GroupedStats_Friend(f, group_value="amount")
	print(g.group())
	print(g.to_bar(save=True))
"""

""" testing GroupedStats with extra_details

	# f = (DescriptionFilter("lecture ") & HasExtraDetailsFilter()).get_filtered_data(b.data)
	# print(len(f))
	# print('\n'.join(map(str,f)))

	# f = AutoFilter("ping pong").get_filtered_data(b.data)
	# f = AutoFilter("ping pong") % b.data
	# print(len(f))
	# print('\n'.join(map(str,f)))
	# print("----------")
	g = TimeCsv.statistics.GroupedStats_Lecture(b.data, group_value="time")
	print(g.group())
	print(g.to_pie(save=False))
"""

""" testing ExtraDetailsGroupedStats

	f = TimeFilter_Month(3) | TimeFilter_Month(4)
	f_data = f.get_filtered_data(b.data)
	print(len(f_data))
	# print('\n'.join(map(str,f_data)))
	g = TimeCsv.statistics.GroupedStats_Homework(f_data, group_value="amount")
	print(g.group())
	# print(g.to_pie(save=False))
"""

""" testing NotFilter

	f1 = AutoFilter("Life")
	f2 = TimeFilter_Days(1)
	# f = f2 & NotFilter(f1)
	f = f2 & ~f1

	f_data = f.get_filtered_data(b.data)
	print(len(f_data))
	print('\n'.join(map(str,f_data)))
"""

""" testing AutoFilter detecting friend

	f1 = AutoFilter("with Mom Dad")
	f2 = TimeFilter_Days(7)
	f = f1 & f2
	f_data = f.get_filtered_data(b.data)
	print(len(f_data))
	print('\n'.join(map(str,f_data)))
"""
