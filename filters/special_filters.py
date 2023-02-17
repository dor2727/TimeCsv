from .content_filters import GroupFilter, DescriptionFilter, DurationFilter

# don't know if I should name them as "SomethingFilter", like the regular filter classes
# or "filter_something", to indicate that it is a specific case and not a general class

filter_podcast = GroupFilter("Podcast") | DescriptionFilter("podcast")

# only "sleep" items, no "more sleep", and only items with more than 3 hours
filter_sleep = GroupFilter("Sleep") & ~DescriptionFilter("more") & DurationFilter(f">{60*60*3}")
filter_sleep = GroupFilter("Sleep") & DescriptionFilter("night") & DurationFilter(f">{60*60*3}")
