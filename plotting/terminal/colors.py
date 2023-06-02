from colorama import Fore, Style

from ...tree.title_types import *

Color = str

H1 = Fore.LIGHTRED_EX
H2 = Fore.LIGHTYELLOW_EX
H3 = Fore.LIGHTGREEN_EX
H4 = Fore.MAGENTA
H5 = Fore.LIGHTMAGENTA_EX

SHADED = Fore.LIGHTBLACK_EX

COLORS = [
	SHADED,
	H1,
	H2,
	H3,
	H4,
	H5,
]

def single_color(s: str, c: Color | int, reset_color: bool=True):
	if isinstance(c, int):
		c = COLORS[c]

	end = Style.RESET_ALL * reset_color
	return c + s + end


COLOR_MAP: dict[type, Color] = {
	MainGroup: H1,
	SubGroup: H2,
	NoneSubGroup: H2,
	Description: H3,
	ExtraDetailsKey: H4,
	ExtraDetailsValue: H5,
}

def colorize(title: Title):
	return single_color(str(title), COLOR_MAP[type(title)])
