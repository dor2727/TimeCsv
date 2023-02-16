import re

def re_escape(x):
	return ''.join(
		(
			'\\'+i
			 if
			i in re.sre_parse.SPECIAL_CHARS
			 else
			i
		)
		for i in x
	)

def re_exact(x):
	return f"\\b{x}\\b"
