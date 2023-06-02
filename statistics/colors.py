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
