import random

from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from pathlib import Path


class OledText:
	"""
	Text helper class for the adafruit_ssd1306 SSD1306 OLED driver.
	Usage example:
		oled = OledText(i2c, 128, 64)
		oled.text("Brave new line", 1)  # Line 1
		oled.text("One more line", 2)  	# Line 2

	Load a display layout:
		oled.config = OledText.layout_64_1big_center()
	"""

	fonts_folder = Path(__file__).parents[0] / "fonts/"

	def __init__(self, i2c, width=128, height=32, auto_show=True, on_draw=None):
		self.disp = adafruit_ssd1306.SSD1306_I2C(width, height, i2c)
		self.width = width
		self.height = height
		self.auto_show = auto_show
		self.layout = {}
		self.on_draw = on_draw

		self.disp.fill(0)
		self.disp.show()

		self.image = Image.new('1', (width, height))

		"""
		self.fontSmall = ImageFont.truetype("fonts/ProggyTiny.ttf", 16) 
		offset = 10 => 3/6 Lines
		"""

		# Default layout for each size
		if height == 32:
			self.layout = OledText.layout_64_5small()
		else:
			self.layout = OledText.layout_64_5small()


	# A set of preset layout definitions

	@staticmethod
	def layout_64_5small():
		""" 5 small text lines for a 64px display. First line with a higher spacing to accomodage yellow line oleds """
		offset = 3
		return {
			1: SmallLine(0, 2),
			2: SmallLine(0, 12 + offset),
			3: SmallLine(0, 24 + offset),
			4: SmallLine(0, 36 + offset),
			5: SmallLine(0, 48 + offset),
		}

	@staticmethod
	def layout_64_1big_3small():
		return {
			1: BigLine(0, 2),
			2: SmallLine(0, 24),
			3: SmallLine(0, 36),
			4: SmallLine(0, 48),
		}

	@staticmethod
	def layout_64_icon_1big_2small():
		return {
			1: BigLine(5, 8, font="FontAwesomeSolid.ttf", size=48),
			2: BigLine(60, 8, font="Arimo.ttf", size=24),
			3: SmallLine(60, 36),
			4: SmallLine(60, 48)
		}

	@staticmethod
	def layout_64_icon_only():
		return {
			1: BigLine(32, 0, font="FontAwesomeSolid.ttf", size=64),
		}

	@staticmethod
	def layout_64_1big_center():
		return {
			1: BigLine(0, 16, font="FreeSans.ttf", size=24)
		}

	@staticmethod
	def layout_64_3medium_3icons():
		return {
			1: BigLine(0, 0),
			2: BigLine(0, 22),
			3: BigLine(0, 44),
			4: BigLine(110, 0, font="FontAwesomeSolid.ttf", size=16),
			5: BigLine(110, 22, font="FontAwesomeSolid.ttf", size=16),
			6: BigLine(110, 44, font="FontAwesomeSolid.ttf", size=16)
		}


	def drawing(self):
		return ImageDraw.Draw(self.image)

	def text(self, text, line=1):

		if line in self.layout:
			self.layout[line].text = text
		else:
			raise KeyError("No line with key '{}' present in the current layout config.", line)

		if self.auto_show:
			self.show()


	def show(self):
		draw = self.drawing()
		# Draw a black filled box to clear the image
		draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

		# Call the onDraw handler
		if self.on_draw is not None:
			self.on_draw(draw)

		for row in self.layout.values():
			draw.text((row.x, row.y), text=row.text, fill=255, font=row.font)

		self.disp.image(self.image)
		self.disp.show()


	def clear(self):
		self.disp.fill(0)
		self.disp.show()


class Line:
	def __init__(self, x, y, font, size):
		self.x = x
		self.y = y
		self.text = ""
		self.font = ImageFont.truetype(str(OledText.fonts_folder / font), size)

class SmallLine(Line):
	def __init__(self, x=0, y=0, font='ProggyClean.ttf', size=16):
		super().__init__(x=x, y=y, font=font, size=size)

class BigLine(Line):
	def __init__(self, x=0, y=0, font='FreeSans.ttf', size=16):
		super().__init__(x=x, y=y, font=font, size=size)



if __name__ == '__main__':

	import time
	from board import SCL, SDA
	import busio

	i2c = busio.I2C(SCL, SDA)

	# Instantiate the display, passing its dimensions (128x64 or 128x32)
	oled = OledText(i2c, 128, 64)

	# A single FontAwesome icon (https://fontawesome.com/cheatsheet/free/solid)
	oled.layout = OledText.layout_64_icon_only()
	oled.text('\uf58b', 1)
	time.sleep(2)

	# Output 5 lines (with auto_draw on, the display is painted after every line)
	oled.layout = OledText.layout_64_5small()
	for i in range(1, 6):
		oled.text("Hello Line {}".format(i), i)
	time.sleep(1)

	# Replacing a single line (keeps the other lines)
	oled.text("Brave new line", 2)
	time.sleep(1)

	# Setting multiple lines with manual .show() (only one display refresh)
	oled.layout = OledText.layout_64_1big_3small()
	oled.auto_show = False
	oled.text("The Title", 1)
	oled.text("Line 2 text", 2)
	oled.text("Line 3 text", 3)
	oled.text("Line 4 text", 4)
	oled.show()
	oled.auto_show = True
	time.sleep(2)

	# A panel with 3 lines and 3 icons to the right
	oled.layout = OledText.layout_64_3medium_3icons()
	oled.auto_show = False
	oled.text("Temperature: ", 1)
	oled.text("Light: ", 2)
	oled.text("Humidity: ", 3)
	oled.text('\uf062', 4)
	oled.text('\uf061', 5)
	oled.text('\uf063', 6)
	oled.show()
	oled.auto_show = True
	time.sleep(0.5)
	oled.text('\uf063', 4)
	time.sleep(2)

	# With a FontAwesome icon (https://fontawesome.com/cheatsheet/free/solid)
	oled.layout = OledText.layout_64_icon_1big_2small()
	oled.auto_show = False
	oled.text('\uf58b', 1)
	oled.text("Meow!", 2)
	oled.text("I am the", 3)
	oled.text("cool cat", 4)
	oled.show()
	oled.auto_show = True
	time.sleep(3)

	# Use a custom display layout
	oled.layout = {
		1: SmallLine(0, 0),
		2: BigLine(5, 15, font="Arimo.ttf", size=24),
		3: BigLine(5, 40, font="Arimo.ttf", size=18)
	}
	oled.text("I want my layout!")
	oled.text("Custom 1", 2)
	oled.text("Custom 2", 3)
	time.sleep(3)

	# Adding own graphics using an onDraw handler
	oled.layout = OledText.layout_64_1big_center()
	oled.on_draw = lambda draw: draw.rectangle((0, 0, 127, 63), outline=255, fill=0)
	oled.text("The Fat Cat", 1)

	time.sleep(4)
	oled.clear()
