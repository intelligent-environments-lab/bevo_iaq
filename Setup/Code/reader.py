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

ser0 = serial.Serial('/dev/ttyUSB0')
ser1 = serial.Serial('/dev/ttyUSB1')

print("hi")

ser0.write(b'\r')
ser0.write(b'\n\r')
line0 = str(ser0.readline(), 'utf-8')
line0 = line0[: -2]
data0 = Data(line0.split(", "))

print(data0)
print('\n')

ser1.write(b'\r')
ser1.write(b'\n\r')
line1 = str(ser1.readline(), 'utf-8')
line1 = line1[: -2]
data1 = Data(line1.split(", "))

print(data1)
print("-------------------------")

ser0.close()
ser1.close()
