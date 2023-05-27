from TimeCsv import DataFolder, \
					GroupFilter, DescriptionFilter, FriendFilter, \
					join_filters_with_or, \
					DetailedStats_AllGroups, DetailedStats_Group
from TimeCsv.consts import DEFAULT_PIE_PATH, DEFAULT_SELECTED_TIME
from TimeCsv.utils import seconds_to_hours_str
from TimeCsv.filters.base_filters import Filter

JSON = {
	 "_group_by": DetailedStats_AllGroups,
	"Console": { "_filter": GroupFilter("GamingConsole"),
				 "_group_by": DetailedStats_Group,
		"Assassin's Creed": {
			"_filter": DescriptionFilter("assassins's creed")
		},
		"Watch Dogs": {
			"_filter": DescriptionFilter("watch dogs")
		},
		"mirror's edge": {
			"_filter": DescriptionFilter("mirror's edge")
		},
		"PS2": {
			"Crash Bandicoot": {
				"_filter": DescriptionFilter("crash bandicoot")
			},
			"Ratchet & Clank": {
				"_filter": DescriptionFilter("ratchet and clank")
			},
		},
	},
	"Solo":    { "_filter": GroupFilter("GamingSolo"   ),},
	"Social":  { "_filter": GroupFilter("GamingSocial" ),},
	"Mobile":  { "_filter": GroupFilter("GamingMobile" ),
				 "_group_by": DetailedStats_Group,
		"Idle": {
			"Afk Arena"    : DescriptionFilter("afk_arena"    ),
			"Idle Heroes"  : DescriptionFilter("idle heroes"  ),
			"Mythic Heroes": DescriptionFilter("mythic heroes"),
		},
		"MOBA": {
			"Wild Rift"     : DescriptionFilter("lol_mobile"    ),
			"Mobile Legends": DescriptionFilter("mobile_legends"),
		}
	},
	"Watch":   { "_filter": GroupFilter("GamingWatch"  ),},
}
