import numpy as np

from scd30_i2c import SCD30 as Sensirion_SCD30

from sps30 import SPS30 as Sensirion_SPS30
import time
from time import sleep


class SPS30:
    # https://pypi.org/project/sps30/
    def __init__(self) -> None:
        sps = Sensirion_SPS30(1)
        sps.start_measurement()
        self.sps = sps

    def scan(self):
        """
        Measures different particulate matter counts and concentrations in the
        room. Data are stored locally and to AWS S3 bucket.
        Returns dictionary containing counts for 0.5, 1, 2.5 , 4, and 10 microns
        in diameter and concentrations for 1, 2.5, 4, and 10 microns in diameter.
        """
        sps = self.sps
        while not sps.read_data_ready_flag():
            time.sleep(0.2)
        try:
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

    # https://pypi.org/project/scd30-i2c/
    def __init__(self) -> None:

        scd30 = Sensirion_SCD30()

        scd30.set_measurement_interval(2)
        scd30.start_periodic_measurement()
        self.scd30 = scd30

    def scan(self):
        """
        Measures the carbon dioxide concentration, temperature, and relative
        humidity in the room. Data are stored locally and to AWS S3 bucket.
        Returns a dictionary containing the carbon dioxide concentration in ppm,
        the temperature in degress Celsius, and the relative humidity as a
        percent.
        """
        scd30 = self.scd30
        while not scd30.get_data_ready():
            time.sleep(0.2)

        try:
            co2, tc, rh = scd30.read_measurement()
        except:
            co2 = np.nan
            tc = np.nan
            rh = np.nan

        return {"CO2": co2, "TC": tc, "RH": rh}
