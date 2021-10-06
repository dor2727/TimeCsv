import os
import re
import datetime

#
# Filesystem paths & extensions
#
DEFAULT_DATA_DIRECTORY  = os.path.expanduser("~/Projects/Projects/TimeCsv/data")
POSSIBLE_FILE_EXTENSIONS = [".tcsv", ".csv", ".txt", ""]
# wget
DAILY_WGET_PATH = os.path.expanduser("~/Projects/TimeCsv/daily_wget.sh")
DAILY_WGET_LOG_PATH = os.path.expanduser("~/Projects/TimeCsv/Telegram_Bot/Logs/daily_wget.log.new")
# temporary files
DEFAULT_PIE_PATH = "/tmp/pie.png"
DEFAULT_BAR_PATH = "/tmp/bar.png"
>>>>>>> main


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
