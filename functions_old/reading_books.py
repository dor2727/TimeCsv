import enum
from TimeCsv import DataFolder, DescriptionFilter, ExtraDetailsFilter, GroupFilter
from TimeCsv.utils import seconds_to_str
from TimeCsv.types import Days, Seconds

read_book_base_filter = GroupFilter("ReadBook") & ~ExtraDetailsFilter("summarise")


class BOOK_FORMAT_TAGS(enum.Enum):
	Physical = enum.auto()
	Audiobook = enum.auto()
	PDF = enum.auto()
class BOOK_CONTENT_TAGS(enum.Enum):
	Novel = enum.auto()
	Self_Improvement = enum.auto()
	Biology = enum.auto()
	Creativity = enum.auto()
	Other = enum.auto()
class BOOK_LEVEL_TAGS(enum.Enum):
	Simple = enum.auto()
	Normal = enum.auto()
	Hardcore = enum.auto()
	Short = enum.auto()
class BOOK_DONE_TAGS(enum.Enum):
	Done = enum.auto()
	Quit_in_the_middle = enum.auto()
	In_progress = enum.auto()

_BOOK_TAG_TYPES = [
	BOOK_FORMAT_TAGS,
	BOOK_CONTENT_TAGS,
	BOOK_LEVEL_TAGS,
	BOOK_DONE_TAGS,
]

_BOOK_TAGS = {
    "on the origin of species": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Biology,
    	BOOK_LEVEL_TAGS.Hardcore,
    	BOOK_DONE_TAGS.Done,
    ],
    "behave - sapolsky": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Biology,
    	BOOK_LEVEL_TAGS.Hardcore,
    	BOOK_DONE_TAGS.Done,
    ],
    "why zebras dont get ulcers": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Biology,
    	BOOK_LEVEL_TAGS.Hardcore,
    	BOOK_DONE_TAGS.Done,
    ],
    "the selfish gene": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Biology,
    	BOOK_LEVEL_TAGS.Hardcore,
    	BOOK_DONE_TAGS.Done,
    ],
    "the blind watchmaker": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Biology,
    	BOOK_LEVEL_TAGS.Hardcore,
    	BOOK_DONE_TAGS.Done,
    ],
    "nature invention": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Biology,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "the cell": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Biology,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "where good ideas come from": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Creativity,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "game theory": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Self_Improvement,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "work hard be nice": [
    	BOOK_FORMAT_TAGS.PDF,
    	BOOK_CONTENT_TAGS.Other,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "internal time": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Self_Improvement,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "the power of habit": [
    	BOOK_FORMAT_TAGS.Audiobook,
    	BOOK_CONTENT_TAGS.Self_Improvement,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "all that you ask": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Novel,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "can i tell you a secret": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Novel,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "when": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Self_Improvement,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "feynman book": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Other,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Quit_in_the_middle,
    ],
    "tough talks": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Self_Improvement,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "atomic habits": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Self_Improvement,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.In_progress,
    ],
    "getting things done": [
    	BOOK_FORMAT_TAGS.PDF,
    	BOOK_CONTENT_TAGS.Self_Improvement,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.In_progress,
    ],
    "digital minimalism": [
    	BOOK_FORMAT_TAGS.Audiobook,
    	BOOK_CONTENT_TAGS.Self_Improvement,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Done,
    ],
    "what happens next": [
    	BOOK_FORMAT_TAGS.Audiobook,
    	BOOK_CONTENT_TAGS.Other,
    	BOOK_LEVEL_TAGS.Simple,
    	BOOK_DONE_TAGS.Done,
    ],
    "poincare": [
    	BOOK_FORMAT_TAGS.PDF,
    	BOOK_CONTENT_TAGS.Creativity,
    	BOOK_LEVEL_TAGS.Short,
    	BOOK_DONE_TAGS.Done,
    ],
    "grit": [
    	BOOK_FORMAT_TAGS.Physical,
    	BOOK_CONTENT_TAGS.Self_Improvement,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.In_progress,
    ],
    "crash test girl": [
    	BOOK_FORMAT_TAGS.Audiobook,
    	BOOK_CONTENT_TAGS.Other,
    	BOOK_LEVEL_TAGS.Normal,
    	BOOK_DONE_TAGS.Quit_in_the_middle,
    ],
    "the 3 days effect": [
    	BOOK_FORMAT_TAGS.Audiobook,
    	BOOK_CONTENT_TAGS.Self_Improvement,
    	BOOK_LEVEL_TAGS.Simple,
    	BOOK_DONE_TAGS.Done,
    ],
    "the last question": [
    	BOOK_FORMAT_TAGS.PDF,
    	BOOK_CONTENT_TAGS.Other,
    	BOOK_LEVEL_TAGS.Short,
    	BOOK_DONE_TAGS.Done,
    ],	
}

def _is_all_tags_valid(tag_list) -> bool:
	if len(tag_list) != len(_BOOK_TAG_TYPES):
		return False

	for cls in _BOOK_TAG_TYPES:
		if not any(isinstance(v, cls) for v in tag_list):
			return False

	return True
assert all(map(_is_all_tags_valid, _BOOK_TAGS.values()))


def get_book_reading_time(all_data, book_name):
	data = DescriptionFilter(book_name) % all_data

	# make sure it's sorted
	data = sorted(data)

	reading_time_bruto: Days = (
		data[-1].date - data[0].date
	).days + 1

	reading_time_neto: Seconds = sum(data)

	print(f"- Book name: {book_name}")
	print(
		f"    Took {reading_time_bruto:3d} days ({len(data)} sessions), in {seconds_to_str(reading_time_neto)}"
		" ; "
		f"      Tags: {[t.name for t in _BOOK_TAGS[book_name]]}"
	)


def get_read_book_statistics(datafolder=None):
	datafolder = datafolder or DataFolder()
	data = read_book_base_filter % datafolder.data

	for book_name in _BOOK_TAGS:
		get_book_reading_time(data, book_name)

if __name__ == '__main__':
	get_read_book_statistics()
