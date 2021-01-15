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

    oled.fill(0)
    oled.text('IAQ', 0, 0)
    oled.text('Beacon', 0, 10)
    oled.show()

if __name__ == '__main__':
    main()