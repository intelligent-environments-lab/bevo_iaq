# Sensor modules
from board import SCL, SDA
from busio import I2C
import dgs
import pigpio
import adafruit_sgp30 as sgp30
import adafruit_tsl2591 as tsl2591

import time

def checkSensirion(address=0x61, bus=1, n=3):
	"""
	Checks connection to Sensirion sensors

	Inputs:
	- address: address of the sensor
	- bus: i2c bus address
	- n: number of bytes to read


	"""
	PIGPIO_HOST = '127.0.0.1'
	pi = pigpio.pi(PIGPIO_HOST)

	h = pi.i2c_open(bus, address)
	print("Connected to device at", str(address))
	count, data = pi.i2c_read_device(h, n)
	print("Data read")
	
	return True

def main():
	# creating i2c bus
	i2c = I2C(SCL, SDA)

	# getting the adafruit sensors
	sgp = sgp30.Adafruit_SGP30(i2c)
	print("Connected to device at", i2c)
	tsl = tsl2591.TSL2591(i2c)
	print("Connected to device at", i2c)

	# getting DGS sensors
	for dev in [0,1]:
		c, _, _ = dgs.takeMeasurement(f"/dev/ttyUSB{dev}")
		if c != -100:
			print("\tDATA READ")

	# getting sensirion sensors
	scd30 = checkSensirion()
	sps30 = checkSensirion(address=0x69)

if __name__ == '__main__':
    main()
