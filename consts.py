import os
import re
import datetime

#
# Filesystem paths & extensions
#
DEFAULT_DATA_DIRECTORY  = os.path.expanduser("~/Dropbox/Projects/TimeCsv/data")
TELEGRAM_DATA_DIRECTORY = os.path.expanduser("~/Dropbox/Projects/TimeCsv/Telegram_Bot/data")
POSSIBLE_FILE_EXTENSIONS = [".tcsv", ".csv", ".txt", ""]
# temporary files
DEFAULT_PIE_PATH = "/tmp/pie.png"
DEFAULT_BAR_PATH = "/tmp/bar.png"


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

EXTRA_DETAILS_SEPERATOR = " ; "


#
# Regex patterns
#
# Regex patterns - friends
#
# a name starts with a capital letter. full names are written without space.
re_cappital_word = "[A-Z][A-Za-z]*"
# names list is
#     Name Name Name and Name
#     which is - at least one
#         where the last one (if there is more than one) is followed by "and"
#         and any name which is not the first nor the last has space before and after itself
PATTERN_NAMES_LIST  = "((%s)( %s)*( and %s)*)" % (tuple([re_cappital_word])*3)
FRIEND_PATTERN_PATTERN_WORDS = ["with", "for", "to"]
FRIEND_PATTERN = [
	re.compile(f"(?<={word} )" + PATTERN_NAMES_LIST)
	for word in FRIEND_PATTERN_PATTERN_WORDS
]
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


#
# Date
#
# how to format [from_day - to_day]
DATE_REPRESENTATION_PATTERN = "%04d/%02d/%02d - %04d/%02d/%02d"
#
DEFAULT_SELECTED_TIME = "All time"
#
NULL_DATE = datetime.datetime(1, 1, 1)
#
WEEK_STARTS_AT_SUNDAY = True
#
RETRY_SLEEP_AMOUNT_IN_HOURS = 1
RETRY_SLEEP_AMOUNT_IN_SECONDS = RETRY_SLEEP_AMOUNT_IN_HOURS * 60 * 60
