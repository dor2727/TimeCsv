from TimeCsv.filters import *

# don't know if I should name them as "SomethingFilter", like the regular filter classes
# or "filter_something", to indicate that it is a specific case and not a general class

filter_podcast = GroupFilter("Podcast") | DescriptionFilter("podcast")

# only "sleep" items, no "more sleep", and only items with more than 3 houts
filter_sleep = DescriptionFilter("sleep") & ~DescriptionFilter("more") & DurationFilter(f">{60*60*3}")
