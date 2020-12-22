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
        ret = "Serial Number:\t" + self.sn + "\nPPB:\t\t" + self.ppb + "\nTemperature:\t" + self.temp + "\nRel. Humidity:\t" + self.rh
        return ret

def takeMeasurement(device, verbose=False):
    '''
    Uses the device string to read data from the serial DGS sensors
    Input:
        - device: string with the devices location - typically USB
    Returns:
        - c: concentration in ppb
        - tc: temperature in degress C
        - rh: relative humidity
    '''

    # Connecting to device
    ser = serial.Serial(device,timeout=5,write_timeout=5)
    print("Connected to device at",device)

    # Getting data from device
    try:
        ser.write(b'\r')
        ser.write(b'\n\r')
        line = str(ser.readline(), 'utf-8')
        line = line[: -2]
        data = Data(line.split(", "))

        if verbose:
            # Outputting
            print("----------------------------")
            print(data)
            print("----------------------------")

        c = data.ppb
        tc = data.temp
        rh = data.rh
        
    except:
        if verbose:
            print('Timeout occurred during write')
        c = -100
        tc = -100
        rh = -100

    # Closing connection and returning relevant data
    ser.close()
    return c, tc, rh
