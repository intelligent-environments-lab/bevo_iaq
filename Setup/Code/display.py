import board
import busio as io

import adafruit_ssd1306

# creating i2c instance
i2c = io.I2C(board.SCL, board.SDA)

# creating sensor object (height, width, i2c object, address (optional))
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

oled.fill(1)
oled.show()