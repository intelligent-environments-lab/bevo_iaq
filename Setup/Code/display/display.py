import os
import glob

import board
import busio as io

import pandas as pd
import numpy as np
import time

import adafruit_ssd1306

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
        measurements.append([df.loc[:,variable].values[-1],u])
     
    return measurements

def main():
    # creating i2c instance
    i2c = io.I2C(board.SCL, board.SDA)

    # creating sensor object (height, width, i2c object, address (optional))
    disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

    #disp.fill(0) # black fill
    #disp.text('IAQ', 0, 0, 1)
    #disp.text('Beacon', 0, 10, 1)
    #disp.show()

    while True:
        # Getting Newest Measurements
        # ---------------------------
        m2 = get_measurements(sensor_type="sensirion",variables=["CO2","PM_C_2p5"],units=["ppm","ug/m3"])
        m3 = get_measurements(sensor_type="adafruit",variables=["Lux","TVOC","NO2","CO","T_NO2"],units=["lux","ppb","ppb","ppm","C"])
        m = m2+m3 # combining measurements

        # Displaying Measurements
        # -----------------------
        for value, unit in m:
            disp.text(f"{value} {unit}",0,0,1)
            disp.show()
            time.sleep(1000)

if __name__ == '__main__':
    main()