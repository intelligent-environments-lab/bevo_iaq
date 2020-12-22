# Sensor modules
from board import SCL, SDA
from busio import I2C
import dgs
import pigpio
import adafruit_sgp30 as sgp30
import adafruit_tsl2591 as tsl2591

import time

# creating i2c bus
i2c = I2C(SCL, SDA)

# getting the adafruit sensors
sgp = sgp30.Adafruit_SGP30(i2c)
tsl = tsl2591.TSL2591(i2c)

# getting DGS sensors
no2, _, _ = dgs.takeMeasurement("/dev/ttyUSB0")
co, _, _ = dgs.takeMeasurement("/dev/ttyUSB1")

# getting sensirion sensors
scd30 = checkSensirion()
sps30 = checkSensirion(I2C_SLAVE=0x69):

def checkSensirion(I2C_SLAVE=0x61, I2C_BUS=1, n=18):
	"""

	"""
	PIGPIO_HOST = '127.0.0.1'
	pi = pigpio.pi(PIGPIO_HOST)

	h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
	count, data = pi.i2c_read_device(h, n)

	return True
