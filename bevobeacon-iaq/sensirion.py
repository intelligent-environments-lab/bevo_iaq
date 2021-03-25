"""Sensirion Sensors

This script handles data measurements from the Sensirion SCD30 and SPS30 sensors.
"""
import time
import asyncio
import numpy as np

# pip packages
from scd30_i2c import SCD30 as Sensirion_SCD30
from sps30 import SPS30 as Sensirion_SPS30


class SPS30:
    def __init__(self) -> None:
        sps = Sensirion_SPS30(1)
        self.sps = sps

    def enable(self):
        self.sps.start_measurement()

    def disable(self):
        self.sps.stop_measurement()

    async def scan(self):
        """
        Measures different particulate matter counts and concentrations in the
        room. Data are stored locally and to AWS S3 bucket.
        Returns dictionary containing counts for 0.5, 1, 2.5 , 4, and 10 microns
        in diameter and concentrations for 1, 2.5, 4, and 10 microns in diameter.
        """
        sps = self.sps
        try:
            # Wait until data ready flag is shown but limit retries so it doesn't block forever
            attempts = 0
            while (not sps.read_data_ready_flag()) and attempts <= 3:
                await asyncio.sleep(0.1)
                attempts += 1

            # Read data
            sps.read_measured_values()
            pm = sps.dict_values
        except:
            pm = {
                "nc0p5": np.nan,
                "nc1p0": np.nan,
                "nc2p5": np.nan,
                "nc4p0": np.nan,
                "nc10p0": np.nan,
                "pm1p0": np.nan,
                "pm2p5": np.nan,
                "pm4p0": np.nan,
                "pm10p0": np.nan,
            }

        return {
            "pm_n_0p5": pm["nc0p5"],
            "pm_n_1": pm["nc1p0"],
            "pm_n_2p5": pm["nc2p5"],
            "pm_n_4": pm["nc4p0"],
            "pm_n_10": pm["nc10p0"],
            "pm_c_1": pm["pm1p0"],
            "pm_c_2p5": pm["pm2p5"],
            "pm_c_4": pm["pm4p0"],
            "pm_c_10": pm["pm10p0"],
        }


class SCD30:
    def __init__(self) -> None:
        scd30 = Sensirion_SCD30()
        self.scd30 = scd30

    def enable(self):
        self.scd30.start_periodic_measurement()

    def disable(self):
        self.scd30.stop_periodic_measurement()

    async def scan(self):
        """
        Measures the carbon dioxide concentration, temperature, and relative
        humidity in the room. Returns a dictionary containing the carbon dioxide concentration in ppm,
        the temperature in degress Celsius, and the relative humidity as a
        percent.
        """
        scd30 = self.scd30
        try:

            # Wait until data ready flag is shown but limit retries so it doesn't block forever
            attempts = 0
            while (not scd30.get_data_ready()) and (attempts <= 3):
                await asyncio.sleep(0.1)
                attempts += 1

            # Read data
            co2, tc, rh = scd30.read_measurement()
        except:
            co2 = np.nan
            tc = np.nan
            rh = np.nan

        return {"CO2": co2, "TC": tc, "RH": rh}
