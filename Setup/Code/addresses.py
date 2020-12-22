# Sensor modules
from board import SCL, SDA
from busio import I2C
import dgs
import pigpio
import adafruit_sgp30 as sgp30
import adafruit_tsl2591 as tsl2591

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

def readingOutput(measurment,threshold):
	"""
	Outputs an error or success message
	"""
	if measurment <= threshold:
		print("\tERROR READING FROM SENSOR")
	else:
		print("\tDATA READ")

def checkAdafruit(sensor_name="sgp30"):
	"""
	Checks connection to Adafruit sensors
	"""
	# creating i2c bus
	i2c = I2C(SCL, SDA)

	if sensor_name == "sgp30":
		sgp = sgp30.Adafruit_SGP30(i2c)
		print("Connected to device at")
		# Getting measurment
		sgp.iaq_init()
		_, tvoc = sgp.iaq_measure()
		readingOutput(tvoc,0)
	elif sensor_name == "tsl2591":
		tsl = tsl2591.TSL2591(i2c)
		print("Connected to device at")
		# Getting measurment
		tsl.enabled = True
		time.sleep(1)
		lux = tsl.lux
		readingOutput(lux,-1)
	else:
		print(f"Sensor {sensor_name} does not exist.")

	print(i2c.scan())

def checkDGS(dev_no=0):
	"""
	Checks connection to DGS sensors
	"""
	c, _, _ = dgs.takeMeasurement(f"/dev/ttyUSB{dev_no}")
	readingOutput(c,-10)

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
	else:
		print("\tERROR READING FROM SENSOR")

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
	for address in [0x61,0x69]:
		time.sleep(0.5)
		checkSensirion(address=address)

if __name__ == '__main__':
    main()
