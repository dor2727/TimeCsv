from functools import partial
from colorama import Fore, Style

Color = str

H1 = Fore.LIGHTRED_EX
H2 = Fore.LIGHTYELLOW_EX
H3 = Fore.LIGHTGREEN_EX
H4 = Fore.MAGENTA

SHADED = Fore.LIGHTBLACK_EX

COLORS = [
	SHADED,
	H1,
	H2,
	H3,
	H4,
]

def single_color(s: str, c: Color | int, reset_color: bool=True):
	if isinstance(c, int):
		c = COLORS[c]

	end = Style.RESET_ALL * reset_color
	return c + s + end

COLORIZE = [
	partial(single_color, c=color)
	for color in COLORS
]
