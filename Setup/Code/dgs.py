#!/usr/bin/python3

import serial

class Data:
    def __init__(self, split):
        self.sn             = split[0]
        self.ppb            = split[1]
        self.temp           = split[2]
        self.rh             = split[3]
        self._rawSensor     = split[4]
        self._tempDigital   = split[5]
        self._rhDigital     = split[6]
        self.day            = split[7]
        self.hour           = split[8]
        self.min            = split[9]
        self.sec            = split[10]

    def __str__(self):
        ret = "Serial Number:\t" + self.sn + "\nPPB:\t\t" + self.ppb + "\nTemperature:\t" + self.temp + "\nRel. Humidity:\t" + self.rh +"\n"
        return ret

def takeMeasurement(device):
    '''
    Uses the device string to read data from the serial DGS sensors
    Input:
        - device: string with the devices location - typically USB
    Returns:
        - data.c: concentration in ppb
        - data.temp: temperature in degress C
        - data.rh: relative humidity
    '''

    # Connecting to device
    ser = serial.Serial(device)
    print("Connected to device at",device)

    # Getting data from device
    ser.write(b'\r')
    ser.write(b'\n\r')
    line = str(ser.readline(), 'utf-8')
    line = line[: -2]
    data = Data(line.split(", "))

    # Outputting
    print("-------------------------")
    print(data)
    print("-------------------------")

    # Closing connection and returning relevant data
    ser.close()
    return data.ppb, data.temp, data.rh
