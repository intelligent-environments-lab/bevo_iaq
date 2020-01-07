import pigpio # aptitude install python-pigpio
import time
import struct
import sys
import crcmod # aptitude install python-crcmod
import os, signal
from subprocess import call

import pprint
from datetime import datetime
import csv

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

data = [0x00, 0x10, 0x03, 0x00, calcCRC([0x03,0x00])]

try:
	pi.i2c_write_device(h, data)
except Exception as e:
	print("error in i2c_write:", e.__doc__ + ":",  e.value)