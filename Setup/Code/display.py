import board
import busio as io

import adafruit_ssd1306



#oled.fill(1)
#oled.show()

def main():
    # creating i2c instance
    i2c = io.I2C(board.SCL, board.SDA)

    # creating sensor object (height, width, i2c object, address (optional))
    disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

    disp.fill(1)
    disp.show()

    # Setting up display parameters
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    unit_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)

if __name__ == '__main__':
    main()