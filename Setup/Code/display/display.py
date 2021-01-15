import os
import glob

import board
import busio as io

import pandas as pd
import numpy as np
import time

import adafruit_ssd1306
from oled_text import OledText, Layout64, BigLine, SmallLine

def get_measurements(sensor_type,variables,units,path_to_data="/home/pi/DATA"):
    """

    """
    # getting newest file
    file_list = glob.glob(f"{path_to_data}/{sensor_type}/*.csv")
    newest_file = max(file_list, key=os.path.getctime)
    # reading in file
    df = pd.read_csv(f"{newest_file}",index_col=0)
    # getting important var measurements
    measurements = []
    for v, u in zip(variables,units):
        measurements.append([round(df.loc[:,v].values[-1],1),u])
     
    return measurements

def main():
    # creating i2c instance
    i2c = io.I2C(board.SCL, board.SDA)

    # creating sensor object (height, width, i2c object, address (optional))
    oled = OledText(i2c, 128, 64)
    # layout 
    oled.layout = {
        1: SmallLine(0, 0, font="FreeSans.ttf", size=12),
        2: BigLine(5, 20, font="FreeSans.ttf", size=24),
        3: BigLine(80, 24, font="FreeSans.ttf", size=18),
        4: BigLine(70, 20, font="FontAwesomeSolid.ttf",size=10),
        5: SmallLine(100, 20, font="FreeSans.ttf", size=8),
        6: SmallLine(0, 50, font="FreeSans.ttf", size=12),
    }
    oled.text("WCWH",1)
    oled.text("Environment Beacon",6)

    while True:
        # Getting Newest Measurements
        # ---------------------------
        m2 = get_measurements(sensor_type="sensirion",variables=["CO2","PM_C_2p5"],units=["ppm","ug/m"])
        m3 = get_measurements(sensor_type="adafruit",variables=["Lux","TVOC","NO2","CO","T_NO2"],units=["lux","ppb","ppb","ppm","C"])
        m = m2+m3 # combining measurements

        # Displaying Measurements
        # -----------------------
        for value, unit in m:
            oled.text(f"{value}",2)
            oled.text(f"{unit}",3)
            if unit == "C":
                oled.text(f"\uf22d",4)
                oled.text(f"",5)
            elif unit == "ug/m":
                oled.text(f"",4)
                oled.text(f"3",5)
            else:
                oled.text(f"",4)
                oled.text(f"",5)
                
            oled.show()
            time.sleep(2)

if __name__ == '__main__':
    main()