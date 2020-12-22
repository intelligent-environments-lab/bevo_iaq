# Sensor modules
from board import SCL, SDA
from busio import I2C
import dgs
import scd30
import sps30
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
_, _, co2 = scd30.takeMasurement()
n, m = sps30.takeMasurement()