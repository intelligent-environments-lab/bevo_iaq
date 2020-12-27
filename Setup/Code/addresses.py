# Sensor modules
from board import SCL, SDA
from busio import I2C
import dgs
import pigpio
import adafruit_sgp30 as sgp30
import adafruit_tsl2591 as tsl2591

import pandas as pd
import numpy as np

import os
import time
from datetime import datetime, timedelta

def getStatus():
    i2c = I2C(SCL, SDA)
    addrs = i2c.scan()
    time.sleep(1) # sleep to catch any missed addresses
    all_addrs = list(addrs)
    new_addrs = i2c.scan()
    all_addrs.extend(x for x in new_addrs if x not in all_addrs)
    # cross referencing with list of known addresses
    try:
        known_addrs = pd.read_csv("~/bevo_iaq/Setup/Code/known_addresses.csv")
    except FileNotFoundError:
        print("Cannot find file")

    for addr in all_addrs:
        #try:
        name = known_addrs[known_addrs["Hex"] == str(hex(addr))]["Sensor"].values[0]
        variable = known_addrs[known_addrs["Hex"] == str(hex(addr))]["Variable"].values[0]
        if name in ["SCD30","SPS30"]:
            status = checkSensirion(hex(addr))
        elif name in ["SGP30","TSL2591"]:
            status = checkAdafruit(name)
        data = checkData(variable)
        #except:
         #   name = ""
          #  status = ""

        print(f"\t{hex(addr)}\t{name}\t{data}\t{status}")

def checkData(variable):
    """
    Checks the most recent data point for the specified variable
    """
    def get_latest_data_file(log_file="sensirion"):
        """
        Gets the latest data file
        """
        d = datetime.now().strftime("%Y-%m-%d")
        for file in os.listdir(f"./DATA/{log_file}/"):
            if file[4:-4] == d: 
                return pd.read_csv(f"./DATA/{log_file}/{file}",index_col=0,parse_dates=True,infer_datetime_format=True)

        return None

    if variable in ["TVOC","eCO2","Lux","Visible","Infrared","NO2","T_NO2","RH_NO2","CO","T_CO","RH_CO"]:
        df = get_latest_data_file("adafruit")
        # checking to see if last timestep was in the last 15 minutes
        ts = df.index[-1]
        if datetime.now() - timedelta(minutes=15) < ts:
            if df[variable][-1] < 0:
                return "No Recent Data"
            else:
                return "Recent Data Logged"

    elif variable in ["Temperature [C]","Relative Humidity","CO2 PM_N_0p5","PM_N_1","PM_N_2p5","PM_N_4","PM_N_10","PM_C_1","PM_C_2p5","PM_C_4","PM_C_10"]:
        df = get_latest_data_file()
        # checking to see if last timestep was in the last 15 minutes
        ts = df.index[-1]
        if datetime.now() - timedelta(minutes=15) < ts:
            if df[variable][-1] <= 0:
                return "No Recent Data"
            else:
                return "Recent Data Logged"

    else:
        return f"{variable} Not in Data"

def readingOutput(measurment,threshold):
    """
    Outputs an error or success message
    """
    if measurment <= threshold:
        return False
    else:
        #print("\tDATA READ")
        return True

    return False

def checkAdafruit(sensor_name="SGP30"):
    """
    Checks connection to Adafruit sensors
    """
    # creating i2c bus
    i2c = I2C(SCL, SDA)

    if sensor_name == "SGP30":
        try:
            sgp = sgp30.Adafruit_SGP30(i2c)
        except Exception as inst:
            print("Can't Connect to", sensor_name, "-",inst)
            return "Can't Connect"

        time.sleep(1)
        #print("Connected to device at 0x70")
        # Getting measurment
        try:
            sgp.iaq_init()
            time.sleep(1)
            _, tvoc = sgp.iaq_measure()
            read = readingOutput(tvoc,0)
            if read:
                #print("\tSVM30 READY")
                pass
        except:
            return "Cannot Read Data"
    elif sensor_name == "TSL2591":
        try:
            tsl = tsl2591.TSL2591(i2c)
        except Exception as inst:
            print("Can't Connect to", sensor_name, "-",inst)
            return "Can't Connect"

        time.sleep(1)
        #print("Connected to device at 0x29")
        # Getting measurment
        try:
            tsl.enabled = True
            time.sleep(1)
            lux = tsl.lux
            read = readingOutput(lux,-1)
            if read:
                #print("\tTSL2591 READY")
                pass
        except RuntimeError:
            return "Overflow"

    else:
        print(f"Sensor {sensor_name} does not exist.")

    return "Ready"

def checkDGS(dev_no=0):
    """
    Checks connection to DGS sensors
    """
    try:
        c, _, _ = dgs.takeMeasurement(f"/dev/ttyUSB{dev_no}")
    except Exception as inst:
        print("Can't Connect to", dev_no, "-",inst)
        return "Can't Connect"

    try:
        read = readingOutput(float(c),-10)
        if read:
            #print(f"\tSPEC{dev_no} READY")
            pass
    except:
        return "Cannot Read Data"

    return "Ready"

def checkSensirion(address=0x61, bus=1, n=3):
    """
    Checks connection to Sensirion sensors

    Inputs:
    - address: address of the sensor
    - bus: i2c bus address
    - n: number of bytes to read
    """
    # Connect to sensor
    try:
        print(address)
        PIGPIO_HOST = '127.0.0.1'
        pi = pigpio.pi(PIGPIO_HOST)
        h = pi.i2c_open(int(bus), address)
    except Exception as inst:
        print("Connected to device at", address, "-",inst)
        return "Can't Connect"

    count, data = pi.i2c_read_device(h, n)
    if data:
        #print("\tDATA READ")
        pass
    else:
        #print("\tERROR READING FROM SENSOR")
        return "Cannot Read Data"

    h.i2c_close()
    pi.stop()
    return "Ready"

def main():
    
    getStatus()

if __name__ == '__main__':
    main()
