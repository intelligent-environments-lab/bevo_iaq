from oled_text import BigLine, SmallLine

def layout_3small():
	""" 3 small text lines for a 32px display. """
	return {
		1: SmallLine(0, 0),
		2: SmallLine(0, 10),
		3: SmallLine(0, 20)
	}


def layout_1big_1small():
	""" 1 big, 1 small text lines for a 32px display. """
	return {
		1: BigLine(0, 0, font='Arimo.ttf', size=18),
		2: SmallLine(0, 19),
	}


def layout_2medium():
	""" 2 medium text lines for a 32px display. """
	return {
		1: BigLine(0, 1, font='FreeSans.ttf', size=14),
		2: BigLine(0, 17, font='FreeSans.ttf', size=14)
	}


def layout_1big():
	""" 1 big text line for a 32px display. """
	return {
		1: BigLine(0, 8, font='FreeSans.ttf', size=20),
	}


def layout_iconleft_1big():
	""" Icon left plus 1 big text lines for a 32px display. """
	return {
		1: BigLine(0, 8, font="FontAwesomeSolid.ttf", size=24),
		2: BigLine(26, 10, font='FreeSans.ttf', size=20),
	}


def layout_iconright_1big():
	""" Icon right plus 1 big text lines for a 32px display. """
	return {
		1: BigLine(100, 8, font="FontAwesomeSolid.ttf", size=24),
		2: BigLine(0, 10, font='FreeSans.ttf', size=20),
	}
