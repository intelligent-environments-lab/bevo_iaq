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
			from oled_text import Layout32
			self.layout = Layout32.layout_3small()
		else:
			from oled_text import Layout64
			self.layout = Layout64.layout_5small()


	def drawing(self):
		return ImageDraw.Draw(self.image)

	def text(self, text, line=1):

		if line in self.layout:
			self.layout[line].text = str(text)
		else:
			raise KeyError("No line with key '{}' present in the current layout config.".format(line))

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
	""" Represents a line on the oled display """
	def __init__(self, x, y, font, size):
		self.x = x
		self.y = y
		self.text = ""
		try:
			self.font = ImageFont.truetype(str(OledText.fonts_folder / font), size)
		except OSError:
			self.font = ImageFont.truetype(str(font), size)

class SmallLine(Line):
	""" A small display line preset (using ProggyClean.ttf) """
	def __init__(self, x=0, y=0, font='ProggyClean.ttf', size=16):
		super().__init__(x=x, y=y, font=font, size=size)

class BigLine(Line):
	""" A big display line preset (using FreeSans.ttf) """
	def __init__(self, x=0, y=0, font='FreeSans.ttf', size=16):
		super().__init__(x=x, y=y, font=font, size=size)

