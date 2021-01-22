import os
import glob

import board
import busio as io

import pandas as pd
import time

from oled_text import OledText, BigLine, SmallLine

def get_measurements(sensor_type,variables,units,names,path_to_data="/home/pi/DATA"):
    """
    Gets the latest measurements from the data file

    Inputs:
    - sensor_type: string in ["adafruit","sensirion"]
    - variables: list of strings of raw variable name(s) in the data dataframe columns
    - units: list of strings of units for variable(s)
    - names: list of strings of display name(s) for the variables
    - path_to_data: string for the path to the sensirion/adafruit directories

    Returns a list of lists where the inner list corresponds to the variable, unit, and display name
    """
    # getting newest file
    file_list = glob.glob(f"{path_to_data}/{sensor_type}/*.csv")
    newest_file = max(file_list, key=os.path.getctime)
    beacon = int(newest_file.split("/")[-1][1:3])
    print(beacon)
    # reading in file
    df = pd.read_csv(f"{newest_file}",index_col=0)
    # getting important var measurements
    measurements = []
    for v, u, n in zip(variables,units,names):
        value = round(df.loc[:,v].values[-1],1)
        # correcting the value 
        for file in os.listdir(f"/home/pi/bevo_iaq/Setup/Code/correction/"):
            file_info = file.split("-")
            if file_info[0] == v.lower():
                correction = pd.read_csv(f"/home/pi/bevo_iaq/Setup/Code/correction/{file}",index_col=0)
            else:
                correction = pd.DataFrame(data={"beacon":np.arange(1,51),"constant":np.zeros(51),"coefficient":np.ones(51)}).set_index("beacon")
        
        value = value * correction.loc[beacon,"coefficient"] + correction.loc[beacon,"constant"]
        measurements.append([value,u,n])
    
    print(measurements)
    return measurements

def main():
    # creating i2c instance
    i2c = io.I2C(board.SCL, board.SDA)

    # creating sensor object (i2c object, height, width)
    oled = OledText(i2c, 128, 64)
    # layout 
    oled.layout = {
        1: SmallLine(2, 4, font="FreeSans.ttf", size=12), # title
        2: BigLine(5, 20, font="FreeSans.ttf", size=24), # value
        3: BigLine(80, 24, font="FreeSans.ttf", size=18), # unit
        4: BigLine(74, 20, font="FontAwesomeSolid.ttf",size=10), # degree
        5: SmallLine(120, 20, font="FreeSans.ttf", size=8), # exponent
        6: SmallLine(2, 50, font="FreeSans.ttf", size=12), # name
    }
    oled.text("WCWH BEVO Beacon",1)

    while True:
        # Getting Newest Measurements
        # ---------------------------
        m2 = get_measurements(sensor_type="sensirion",variables=["CO2","PM_C_2p5"],
            units=["ppm","ug/m"],names=["Carbon Dioxide", "Particulate Matter"])
        m3 = get_measurements(sensor_type="adafruit",variables=["Lux","TVOC","NO2","CO","T_NO2"],
            units=["lux","ppb","ppb","ppm","C"],names=["Light Level", "Nitrogen Dioxide","TVOCs","Carbon Monoxide","Temperature"])
        m = m2+m3 # combining measurements

        # Displaying Measurements
        # -----------------------
        try:
            for value, unit, name in m:
                if name == "Carbon Monoxide": # converting raw CO measurements to ppm
                    value /= 1000
                    value = round(value,1)

                oled.text(f"{value}",2) # output of measured value
                oled.text(f"{unit}",3) # output of the variable
                if unit in ["C","F"]: # adding degree symbol for temperature
                    oled.text(f"\uf22d",4)
                    oled.text(f"",5)
                elif unit == "ug/m": # adding exponent for pm
                    oled.text(f"",4)
                    oled.text(f"3",5)
                else: # no output on these "lines"
                    oled.text(f"",4)
                    oled.text(f"",5)

                oled.text(f"{name}",6) # output of the display name

                oled.show()
                time.sleep(2) # holding display for 2 seconds
        except OSError:
            oled.clear()
            oled.text(f"ERROR",3)
            time.sleep(3)

# Execution Start
# ------------------------------------------------------------------------- #
try:
    main()
except:
    print("ERROR")

# ------------------------------------------------------------------------- #