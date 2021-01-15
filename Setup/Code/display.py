import board
import busio as io

import adafruit_ssd1306

def main():
    # creating i2c instance
    i2c = io.I2C(board.SCL, board.SDA)

    # creating sensor object (height, width, i2c object, address (optional))
    disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

    disp.fill(0)
    disp.text('IAQ', 0, 0, 1)
    disp.text('Beacon', 0, 10, 1)
    disp.show()

if __name__ == '__main__':
    main()