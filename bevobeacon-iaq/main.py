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

# AWS libraries
import boto3
from botocore.exceptions import ClientError

async def main(beacon = '00'):
    # AWS credentials
    try:
        AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
        AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
        BUCKET_NAME = os.environ['BUCKET_NAME']
    except KeyError:
        # credentials have not been specified
        AWS_ACCESS_KEY_ID = ""
        AWS_SECRET_ACCESS_KEY = ""
        BUCKET_NAME = ""

    s3 = boto3.client(
        's3',
        aws_access_key_id = AWS_ACCESS_KEY_ID,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
    )
    # upload variables
    S3_CALL_TIMESTAMP = datetime.datetime.now()
    S3_CALL_FREQUENCY = datetime.timedelta(minutes=5)
    S3_FILEPATH = f"B{beacon}/"
   
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

    # These sensors are to turn on and off after each scan cycle to save power
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
        df.sort_index(axis=1,inplace=True)
        log.info(df)

        # Write data to csv file
        filename = f'/home/pi/DATA/b{beacon}_{date.strftime("%Y-%m-%d")}.csv'
        try:
            if os.path.isfile(filename):
                df.to_csv(filename, mode="a", header=False)
                log.info(f"Data appended to {filename}")
            else:
                # create file locally
                df.to_csv(filename)
                log.info(f"Data written to {filename}")
        except Exception as e:
            log.warning(e)

        # Write data to S3
        if datetime.datetime.now() - S3_CALL_TIMESTAMP >= S3_CALL_FREQUENCY:
            # upload raw data
            aws_s3_upload_file(s3 = s3,
                filename=filename,
                s3_bucket=BUCKET_NAME,
                s3_filepath=S3_FILEPATH
            )
            # upload summary statistics
            ## first generate the file
            os.systemf("python3 /home/pi/bevobeacon-iaq/calculate_summary_stats.py {beacon}")
            ## send to S3
            aws_s3_upload_file(s3 = s3,
                filename=f'/home/pi/summary_stats/b{beacon}-summary-{date.strftime("%Y-%m-%d")}.csv',
                s3_bucket=BUCKET_NAME,
                s3_filepath=S3_FILEPATH
            )

            S3_CALL_TIMESTAMP = datetime.datetime.now()
            log.info("Data uploaded to S3")
        else:
            log.info("Upload to S3 bucket delayed.")

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

def aws_s3_upload_file(s3,filename,s3_bucket,s3_filepath):
	"""
	Uploads locally stored file to AWS S3 bucket.
    
    Parameters
    ----------
	filename: str
        full filepath of the local file
	s3_bucket: str
        name of the target bucket
	s3_filepath: str
        specifies the target location of the file in the bucket
	
    Returns
    -------
    <void>
	"""
	try:
		s3_filename = s3_filepath + format(filename.split('/')[-1])
		s3.upload_file(filename, s3_bucket, s3_filename)
		logging.debug(filename, 'was uploaded to', s3_bucket)
		log.info(f"{filename} was uploaded to AWS S3 bucket: {s3_bucket}")
	except ClientError as e:
		logging.error(e)
		log.info(e)
	except FileNotFoundError as e:
		logging.error(e)
		log.info(e)

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
