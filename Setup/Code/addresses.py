# Sensor modules
from board import SCL, SDA
from busio import I2C
import dgs
import pigpio
import adafruit_sgp30 as sgp30
import adafruit_tsl2591 as tsl2591

import pandas as pd
import numpy as np

import time

def getI2CAddresses():
	i2c = I2C(SCL, SDA)
	addrs = i2c.scan()
	time.sleep(1) # sleep to catch any missed addresses
	all_addrs = list(addrs)
	new_addrs = i2c.scan()
	all_addrs.extend(x for x in new_addrs if x not in all_addrs)
	print("Available Addresses:")
	for addr in all_addrs:
		print(f"\t{hex(addr)}")

	# cross referencing with list of known addresses
	try:
		known_addrs = pd.read_csv("./known_addresses.csv")
	except ImportError:
		pass

def readingOutput(measurment,threshold):
	"""
	Outputs an error or success message
	"""
	if measurment <= threshold:
		print("\tERROR READING FROM SENSOR")
	else:
		print("\tDATA READ")
		return True

	return False

def checkAdafruit(sensor_name="sgp30"):
	"""
	Checks connection to Adafruit sensors
	"""
	# creating i2c bus
	i2c = I2C(SCL, SDA)

	if sensor_name == "sgp30":
		sgp = sgp30.Adafruit_SGP30(i2c)
		print("\nSVM30")
		print("Connected to device at 0x70")
		# Getting measurment
		sgp.iaq_init()
		_, tvoc = sgp.iaq_measure()
		read = readingOutput(tvoc,0)
		if read:
			print("\tSVM30 READY")
	elif sensor_name == "tsl2591":
		tsl = tsl2591.TSL2591(i2c)
		print("Connected to device at 0x29")
		# Getting measurment
		tsl.enabled = True
		time.sleep(1)
		lux = tsl.lux
		read = readingOutput(lux,-1)
		if read:
			print("\tTSL2591 READY")
	else:
		print(f"Sensor {sensor_name} does not exist.")

def checkDGS(dev_no=0):
	"""
	Checks connection to DGS sensors
	"""
	c, _, _ = dgs.takeMeasurement(f"/dev/ttyUSB{dev_no}")
	read = readingOutput(float(c),-10)
	if read:
		print(f"SPEC{dev_no} READY")

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
	print("Connected to device at", address)
	count, data = pi.i2c_read_device(h, n)
	if data:
		print("\tDATA READ")
		return True
	else:
		print("\tERROR READING FROM SENSOR")

	return False

def main():
	getI2CAddresses()

	# getting the adafruit sensors
	for sensor in ["sgp30","tsl2591"]:
		time.sleep(0.5)
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
			print(f"{sensor} READY")

if __name__ == '__main__':
    main()
