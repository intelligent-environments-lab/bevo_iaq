import pigpio # aptitude install python-pigpio
import time
import struct
import sys
import crcmod # aptitude install python-crcmod
import os, signal
from subprocess import call

from datetime import datetime

def calcCRC(TwoBdataArray):
	byteData = ''.join(chr(x) for x in TwoBdataArray)
	return f_crc8(byteData)

def calcFloat(sixBArray):
	struct_float = struct.pack('>BBBB', sixBArray[0], sixBArray[1], sixBArray[3], sixBArray[4])
	float_values = struct.unpack('>f', struct_float)
	first = float_values[0]
	return first

def printHuman(data):
	print("Concentration (ug/m3)")
	print("---------------------------------------")
	print("PM1: {0:.3f}\tPM2.5: {0:.3f}\tPM4: {0:.3f}\tPM10: {0:.3f}".format(calcFloat(data), calcFloat(data[6:12]), calcFloat(data[12:18]), calcFloat(data[18:24])))
	print("Count (#/L)")
	print("---------------------------------------")
	print("PM0.5 count: {0:.3f}".format(calcFloat(data[24:30])))
	print("PM1   count: {0:.3f}".format(calcFloat(data[30:36])))
	print("PM2.5 count: {0:.3f}".format(calcFloat(data[36:42])))
	print("PM4   count: {0:.3f}".format(calcFloat(data[42:48])))
	print("PM10  count: {0:.3f}".format(calcFloat(data[48:54])))
	print("---------------------------------------")
	print("Typical Size: {0:.3f}".format(calcFloat(data[54:60])))
	print("---------------------------------------")

# Setting up communication
PIGPIO_HOST = '127.0.0.1'
I2C_SLAVE = 0x69
I2C_BUS = 1

# Checking to see if device is found
deviceOnI2C = call("i2cdetect -y 1 0x69 0x69|grep '\--' -q", shell=True) # grep exits 0 if match found
if deviceOnI2C:
	print("I2Cdetect found SPS30")
else:
	print("SPS30 (0x69) not found on I2C bus")

pi = pigpio.pi(PIGPIO_HOST)

h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
f_crc8 = crcmod.mkCrcFun(0x131, 0xFF, False, 0x00)

# Trying to start measurement
pi.i2c_write_device(h, [0x00, 0x10, 0x03, 0x00, calcCRC([0x03,0x00])])
while True:
	# Seeing if data is ready
	ret = pi.i2c_write_device(h,[0x02, 0x02])
	print(ret)
	# Reading data from sensor
	ret = pi.i2c_write_device(h,[0x03,0x00])
	print(ret)
	(count, data) = pi.i2c_read_device(h,59)
	# Outputting data
	print("Number of bytes:",count)
	printHuman(data)
	print()
	time.sleep(10)
