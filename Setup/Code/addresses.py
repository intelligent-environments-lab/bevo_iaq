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

def getStatus():
    i2c = I2C(SCL, SDA)
    addrs = i2c.scan()
    time.sleep(1) # sleep to catch any missed addresses
    all_addrs = list(addrs)
    new_addrs = i2c.scan()
    all_addrs.extend(x for x in new_addrs if x not in all_addrs)
    # cross referencing with list of known addresses
    try:
        known_addrs = pd.read_csv("./bevo_iaq/Setup/Code/known_addresses.csv")
    except FileNotFoundError:
        print("Cannot find file")

    for addr in all_addrs:
        try:
            name = known_addrs[known_addrs["Hex"] == str(hex(addr))]["Sensor"].values[0]
            if name in ["SCD30","SPS30"]:
                status = checkSensirion(hex(addr))
            elif name in ["SGP30","TSL2591"]:
                status = checkAdafruit(name)
        except:
            name = ""
            status = ""

        print(f"\t{hex(addr)}\t{name}\t{status}")

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
        except:
            return "No Sensor Detected"

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
    elif sensor_name == "tsl2591":
        try:
            tsl = tsl2591.TSL2591(i2c)
        except:
            return "No Sensor Detected"

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
    except:
        return "No Sensor Detected"

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
        PIGPIO_HOST = '127.0.0.1'
        pi = pigpio.pi(PIGPIO_HOST)
        h = pi.i2c_open(bus, address)
    except Exception as inst:
        #print("Connected to device at", address)
        return "No Sensor Detected"

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

def old():
    # getting the adafruit sensors
    for sensor in ["sgp30","tsl2591"]:
        time.sleep(1)
        checkAdafruit(sensor)

    # getting DGS sensors
    for dev in [0,1]:
        time.sleep(0.5)
        checkDGS(dev)

    # getting sensirion sensors
    for address, sensor in zip([0x61,0x69],["SCD30","SPS30"]):
        time.sleep(0.5)
        read = checkSensirion(address=address)
        if read:
            print(f"\t{sensor} READY")

if __name__ == '__main__':
    main()
