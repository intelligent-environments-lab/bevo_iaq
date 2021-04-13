from oled_text import BigLine, SmallLine


def layout_5small():
	""" 5 small text lines for a 64px display. First line with a higher spacing to accomodage yellow line oleds """
	offset = 3
	return {
		1: SmallLine(0, 2),
		2: SmallLine(0, 12 + offset),
		3: SmallLine(0, 24 + offset),
		4: SmallLine(0, 36 + offset),
		5: SmallLine(0, 48 + offset),
	}


def layout_1big_3small():
	return {
		1: BigLine(0, 2),
		2: SmallLine(0, 24),
		3: SmallLine(0, 36),
		4: SmallLine(0, 48),
	}


def layout_icon_1big_2small():
	return {
		1: BigLine(5, 8, font="FontAwesomeSolid.ttf", size=48),
		2: BigLine(60, 8, font="Arimo.ttf", size=24),
		3: SmallLine(60, 36),
		4: SmallLine(60, 48)
	}


def layout_icon_only():
	return {
		1: BigLine(32, 0, font="FontAwesomeSolid.ttf", size=64),
	}


def layout_1big_center():
	return {
		1: BigLine(0, 16, font="FreeSans.ttf", size=24)
	}


def layout_3medium_3icons():
	return {
		1: BigLine(0, 0),
		2: BigLine(0, 22),
		3: BigLine(0, 44),
		4: BigLine(110, 0, font="FontAwesomeSolid.ttf", size=16),
		5: BigLine(110, 22, font="FontAwesomeSolid.ttf", size=16),
		6: BigLine(110, 44, font="FontAwesomeSolid.ttf", size=16)
	}

