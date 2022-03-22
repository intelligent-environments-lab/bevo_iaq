"""Adafruit Sensors

This script handles data measurements from the Adafruit SGP30 and TSL2591 sensors.
"""
import asyncio
import time
import numpy as np

# Raspberry PI board libraries
from board import SCL, SDA
from busio import I2C

# Sensor libraries
import adafruit_sgp30
import adafruit_tsl2591


class SGP30:
    """Located within SVM30"""

    def __init__(self) -> None:
        i2c = I2C(SCL, SDA)
        sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
        sgp30.iaq_init()
        self.sgp30 = sgp30

    async def scan(self):
        try:
            eCO2, TVOC = self.sgp30.iaq_measure()
        except:
            eCO2 = np.nan
            TVOC = np.nan

        data = {"total_volatile_organic_compounds-ppb": TVOC, "equivalent_carbon_dioxide-ppm": eCO2}
        return data


class TSL2591:
    def __init__(self) -> None:
        i2c = I2C(SCL, SDA)
        tsl = adafruit_tsl2591.TSL2591(i2c)

        # set gain and integration time; gain 0 = 1x & 1 = 16x. Integration time of 1 = 101ms
        tsl.gain = 0
        tsl.integration_time = 1  # 101 ms intergration time.

        self.tsl = tsl

    def enable(self):
        self.tsl.enabled = True

    def disable(self):
        self.tsl.enabled = False

    async def scan(self):
        try:
            tsl = self.tsl

            # Retrieve sensor scan data
            lux = tsl.lux
            visible = tsl.visible
            infrared = tsl.infrared

            # Check for complete darkness
            if lux == None:
                lux = 0
        except:
            lux = np.nan
            visible = np.nan
            infrared = np.nan

        data = {"visible-unitless": visible, "infrared-unitless": infrared, "light-lux": lux}
        return data