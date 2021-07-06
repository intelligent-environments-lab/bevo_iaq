"""BevoBeacon-IAQ Main Script

This script serves as the entry point for the BevoBeacon sensor data measurement
program. It can be launched from the terminal and runs in a loop until terminated
by the user.

Intelligent Environments Laboratory (IEL), The University of Texas at Austin
Author: Calvin J Lin
Project: Indoor Environmental Quality and Sleep Quality
    - Contact: Hagen Fritz (hagenfritz@utexas.edu)
"""
import os
import sys
import logging
import time
import datetime
import asyncio

import pandas as pd

from adafruit import SGP30, TSL2591
from sensirion import SPS30, SCD30
from spec_dgs import DGS_NO2, DGS_CO


async def main(beacon = '00'):
    sensor_classes = {
        "sgp": SGP30,
        "tsl": TSL2591,
        "sps": SPS30,
        "scd": SCD30,
        "dgs_co": DGS_CO,
        "dgs_no2": DGS_NO2,
    }

    sensors = {}

    # Only use sensors that are available
    for name, sens in sensor_classes.items():
        try:
            sensor = sens()
            sensors.update({name: sensor})
        except Exception as e:
            log.warning(e)

    # These sensors are turn on and off after each scan cycle to save power
    manually_enabled_sensors = list(set(sensors) & set(["tsl", "sps", "scd"]))

    time.sleep(1)  # Wait for all sensors to be initialized

    log.info(f"Successfully created: {sensors.keys()}")
    log.info("Attempting scans")

    starttime = time.time()  # Used for preventing time drift
    while True:
        start_time = time.time()  # Used for evaluating scan cycle time performance

        # Turn on all sensors before starting scans
        for manual_sensor in manually_enabled_sensors:
            try:
                sensors[manual_sensor].enable()
            except:
                log.warning(f"Sensor {manual_sensor} not enabled")

        # Wait for sensors to come online
        time.sleep(0.5)

        data = {}

        async def scan(name):
            """Scans each sensor five times and returns the mean"""
            df = pd.DataFrame(
                [
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                ]
            )
            log.info("\nScan results for " + name)
            log.info(df)
            data[name] = df.mean()
            log.info(data[name])

        # Perform all scans
        await asyncio.gather(*[scan(name) for name in sensors])

        # Combine all data from this cycle into one DataFrame
        date = datetime.datetime.now()
        timestamp = pd.Series({"Timestamp": date.strftime("%Y-%m-%d %H:%M:%S")})
        df = pd.concat([timestamp, *data.values()]).to_frame().T.set_index("Timestamp")
        df = df.rename(
            columns={
                "TC": "Temperature [C]",
                "RH": "Relative Humidity",
                "pm_n_0p5": "PM_N_0p5",
                "pm_n_1": "PM_N_1",
                "pm_n_2p5": "PM_N_2p5",
                "pm_n_4": "PM_N_4",
                "pm_n_10": "PM_N_10",
                "pm_c_1": "PM_C_1",
                "pm_c_2p5": "PM_C_2p5",
                "pm_c_4": "PM_C_4",
                "pm_c_10": "PM_C_10",
            }
        )
        df.sort_index(axis=1,inplace=True)
        log.info(df)

        # Write data to csv file
        filename = f'/home/pi/DATA/b{beacon}_{date.strftime("%Y-%m-%d")}.csv'
        try:
            if os.path.isfile(filename):
                df.to_csv(filename, mode="a", header=False)
                log.info(f"Data appended to {filename}")
            else:
                df.to_csv(filename)
                log.info(f"Data written to {filename}")
        except Exception as e:
            log.warning(e)

        # cleaning SPS
        #sensors["sps"].clean() # 10-second cycle
        #time.sleep(11) # sleep 1 second longer

        # Disable sensors until next measurement interval
        for manual_sensor in manually_enabled_sensors:
            try:
                sensors[manual_sensor].disable()
            except:
                log.warning(f"Sensor {manual_sensor} not disabled")

        # Report cycle time for performance evaluation by user
        elapsed_time = time.time() - start_time
        log.info(f"Cycle Time: {elapsed_time} \n\n")

        # Make sure that interval between scans is exactly 60 seconds
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))

def setup_logger(level=logging.WARNING):
    """logging setup for standard and file output"""
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    log.propagate = False # lower levels are not propogated to children
    if log.hasHandlers():
        log.handlers.clear()
    # stream output
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setLevel(logging.DEBUG)
    sh_format = logging.Formatter("%(message)s")
    sh.setFormatter(sh_format)
    log.addHandler(sh)
    # file output
    f = logging.FileHandler("sensors.log")
    f.setLevel(logging.DEBUG)
    f_format = logging.Formatter("%(asctime)s - %(levelname)s\n%(message)s")
    f.setFormatter(f_format)
    log.addHandler(f)
    return log

if __name__ == "__main__":
    log = setup_logger(logging.INFO)
    beacon = '00'
    asyncio.run(main(beacon = beacon))
