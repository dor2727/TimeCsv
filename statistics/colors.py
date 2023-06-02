from functools import partial
from colorama import Fore, Style

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

def multi_colors(*args, reset_color: bool=True):
	if len(args) % 2 != 0:
		raise ValueError("Should get pairs of (string, color)")

	s = ''
	for i in range(len(args)//2):
		s += single_color(args[i*2], args[i*2+1], reset_color=False)

	return s + Style.RESET_ALL


COLORIZE = [
	partial(single_color, c=color)
	for color in COLORS
]
