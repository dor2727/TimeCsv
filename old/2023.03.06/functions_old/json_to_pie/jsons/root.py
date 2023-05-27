"""
the json is basically a python dictionary
the keys are the names for the pie chart titles
the values are either Filters, or dict, in the latter case, the Filters are joined recursively using `or`

There is always automatically another group named "Other" for all the unmatched categories
"""
from TimeCsv.functions.json_to_pie.jsons.Gaming import JSON as gaming_json
from TimeCsv import GroupFilter


JSON = {
	"Sleep"         : GroupFilter("Sleep"),
	"Work"          : GroupFilter("Work"),
	"Transportation": GroupFilter("Transportation"),
	"Chen"          : GroupFilter("Chen"),
	"Gaming"        : gaming_json,
	"Social"        : {
		"Friends": GroupFilter("Friends"),
		"Family" : GroupFilter("Family"),
	},
	"Life"          : {
		"Life": GroupFilter("Life"),
		"Food": GroupFilter("Food"),
		"Health": GroupFilter("Health"),
		"Sport": GroupFilter("Sport"),
		"Chill": GroupFilter("Chill"),
		"Chores": GroupFilter("Chores"),
	},
}


# unsorted:
#     Read            
#     ReadBook        
#     Watch           
#     Sport           
#     Programming     
#     Youtube     
#     Blog            
#     Organize        
#     Puzzle          
#     Study           
#     Time            
#     Computer        
#     Shopping        
#     Wait            
#     Moneycsv        
#     Think           
#     Meditate        
#     Reddit          
#     GamingWatch     
#     Hobbies         
#     Discord         
#     Mail            
