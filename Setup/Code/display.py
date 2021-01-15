import board
import busio as io

import adafruit_ssd1306

# creating i2c instance
i2c = io.I2C(board.SCL, board.SDA)

# creating sensor object (height, width, i2c object, address (optional))
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

#oled.fill(1)
#oled.show()

def main():
    disp = adafruit_ssd1306.SSD1306_128_64(rst=None)
    disp.begin()
    disp.clear()
    disp.display()
    disp.fill(0)
    disp.display()

    # Setting up display parameters
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    unit_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)

if __name__ == '__main__':
    main()