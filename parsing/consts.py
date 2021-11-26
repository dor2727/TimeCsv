import re


#
# File format
#
# headers to look for in every csv
BASE_HEADERS = ["Date", "Start", "Stop", "Group", "Description"]
# Date parsing
COPY_LAST_DATE             = "----/--/--"
ADD_LAST_DATE              = "----/--/+1"
SPECIAL_DATE_FORMATS       = [COPY_LAST_DATE, ADD_LAST_DATE]
# start time parsing
COPY_LAST_START_TIME       = "--:--"
SPECIAL_START_TIME_FORMATS = [COPY_LAST_START_TIME]
# stop time parsing
COPY_LAST_STOP_TIME        = "---:--"
SPECIAL_STOP_TIME_FORMATS  = [COPY_LAST_STOP_TIME]
STOP_TIME_INITIALS_STOP     = ('s', 'e') # stop_time can either indicate when the event ended
STOP_TIME_INITIALS_BREAK    = ('b',)     # or how long it lasted
STOP_TIME_INITIALS_DURATION = ('d', 't') + STOP_TIME_INITIALS_BREAK


#
# Extra details
#
EXTRA_DETAILS_SEPERATOR = " ; "
EXTRA_DETAILS_PATTERN_STRIP   = " ?\\(.*?\\)"
	# get both the word before the brackets, and the value of the brackets
EXTRA_DETAILS_PATTERN_EXTRACT = "(\\w+)\\s+\\((.*?)\\)"


#
# Friends
#
# a name starts with a capital letter. full names are written without space.
re_cappital_word = "[A-Z][A-Za-z]*"

# names list is
#     Name Name Name and Name
#     which is - at least one
#         where the last one (if there is more than one) is followed by "and"
#         and any name which is not the first nor the last has space before and after itself
PATTERN_NAMES_LIST  = "((%s)( %s)*( and %s)*)" % (tuple([re_cappital_word])*3)

FRIEND_PATTERN_WORDS = ["with", "for", "to"]

FRIEND_PATTERN_EXTRACT = [
	re.compile(f"(?<={word} ){PATTERN_NAMES_LIST}")
	for word in FRIEND_PATTERN_WORDS
]
FRIEND_PATTERN_STRIP = [
	re.compile(f" ?{word} {PATTERN_NAMES_LIST}")
	for word in FRIEND_PATTERN_WORDS
]
FRIEND_PATTERN_TO_FRIENDS = " to friends"


#
# Regex patterns - location
#
# a location will be wrapped by @ at both ends
# e.g.: go for a walk @ some place @
PATTERN_LOCATION = " ?@ ?(.*?) ?@"
PATTERN_LOCATION_THEIR_PLACE = "@@"
#
# Regex patterns - vehicle
#
VEHICLES = ["bicycle", "car", "foot"]
VEHICLE_PATTERN_STRIP = [
	re.compile(f" ?by {vehicle}")
	for vehicle in VEHICLES
]
