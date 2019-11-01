# **********************************************************************
# The University of Texas at Austin                                    *
# Intelligent Environments Laboratory (IEL)                            *
# Author: Sepehr Bastami					                           *
#	With notable contributions from:			                       *
#	Dr. William Waites					                               *
#	Kingsley Nweye						                               *
# Project: Occupant-Cenetered Control Systems for BAS Integration      *
# Email: sepehr.bastami@utexas.edu                                     *
# **********************************************************************

# Import NOTE: This code can only be executed with a 'Sudo -E python3 <filename.py>'
import time
import csv
import datetime
import os
import traceback

# Import sensor-specific libraries
import adafruit_sgp30
import adafruit_tsl2591
from board import SCL, SDA
from busio import I2C

# AWS libraries
import boto3
from botocore.exceptions import ClientError

# Create I2C Object for sensors
# Also sets setup mode for GPIO to BCM
def createSensor():
    i2c = I2C(SCL, SDA)
    return i2c

#*****************************************
'''NOTICE: CHANGE path + CHANGE bucket name + CHANGE dictionary keys'''
'''NOTICE: turn this off to do testing until figure out AWS database configuration'''

# AWS setup for file upload to S3 bucket.
# AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
# AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
# BUCKET_NAME = os.environ['BUCKET_NAME']
#
# s3 = boto3.client(
#     's3',
#     aws_access_key_id = AWS_ACCESS_KEY_ID,
#     aws_secret_access_key = AWS_SECRET_ACCESS_KEY
# )
# S3_FILEPATH = {
#     'occ': 'RLP/test_beacon/OCC/DATA/occupancy/',
#     'combined': 'RLP/test_beacon/OCC/DATA/combined/'
# }
# S3_CALL_FREQUENCY = datetime.timedelta(minutes=30)
# S3_CALL_TIMESTAMP = {
#     'occ': datetime.datetime.now(),
#     'combined': datetime.datetime.now()
# }
#*****************************************
# File handling
FILEPATH = {
    'combined': '/home/pi/bevobeacon2.0/Setup/Sample_Code/DATA/'
}
filename_writer = {
    'combined': lambda date: FILEPATH['combined'] + date.strftime('%Y-%m-%d') + '_combined.csv'
}

#*****************************************
# import functions for each of the sensors
'''
NOTICE: Should we remove the bled_scan() and button_config()??
'''
def sgp30_scan(i2c):
    # Declare all global variables for use outside the functions
    global eCO2, TVOC
    # Instantiate sgp30 object
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
    # Retrieve sensor scan data
    eCO2, TVOC = sgp30.iaq_measure()
    # Return data
    data = {'TVOC': TVOC, 'eCO2': eCO2}
    return data

def tsl2591_scan(i2c):
    # Declare all global variables for use outside the functions
    global lux, visible, infrared
    # Instantiate tsl object
    tsl = adafruit_tsl2591.TSL2591(i2c)
    # enable sensor and wait a sec for it to get going
    tsl.enabled = True
    time.sleep(1)
    # set gain and integration time; gain 0 = 1x & 1 = 16x. Integration time of 1 = 101ms
    tsl.gain = 0
    tsl.integration_time = 1  # 101 ms intergration time.
    # Retrieve sensor scan data
    lux = tsl.lux
    visible = tsl.visible
    infrared = tsl.infrared
    # Check for complete darkness
    if lux == None:
        lux = 0
    # Disable the sensor and end process
    tsl.enabled = False
    # Return data
    data = {'Visible': visible, 'Infrared': infrared, 'Lux': lux}
    return data

def data_mgmt():
    # Store combined sensor data locally and remotely
    timestamp = datetime.datetime.now()
    data_header = [
        'Timestamp',
        'TVOC',
        'eCO2',
        'Lux',
        'Visible',
        'Infrared'
    ]
    data = [{
        'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'TVOC': TVOC,
        'eCO2': eCO2,
        'Lux': lux,
        'Visible': visible,
        'Infrared': infrared
    }]
    key = 'combined'
    write_csv(
        key=key,
        date=timestamp,
        data_header=data_header,
        data=data
    )

    # Control on S3 call frequency
    '''NOTICE: turn this off to do testing until figure out AWS database configuration'''
    # if timestamp - S3_CALL_TIMESTAMP[key] >= S3_CALL_FREQUENCY:
    #     aws_s3_upload_file(
    #         filename=filename_writer[key](date=timestamp),
    #         s3_bucket=BUCKET_NAME,
    #         s3_filepath=S3_FILEPATH[key]
    #     )
    #     S3_CALL_TIMESTAMP[key] = timestamp
    # else:
    #     print('Upload to S3 bucket delayed.')

def write_csv(key, date, data_header, data):
    '''
    Writes data to csv file. Key is used to decipher the filepath and style of the filename.
    Date filename is used to name & sort files chronologically. Creates a new file if none with
    filename exists or appends to the exsiting file. The data header specifies the field
    names and is a list of the dictionary keys. Data is a list of dictionaries.\n
    key: string\\
    date: datetime.datetime\\
    data_header: list\\
    data: list\\
    return: void
    '''
    filename = filename_writer[key](date=date)
    try:
        if not os.path.isfile(filename):
            # First update s3 bucket with latest version of last created file
            history_limit = 10 # Days
            for i in range(1,history_limit):
                history_date = date - datetime.timedelta(days=i)
                history_file = filename_writer[key](date=history_date)
                '''NOTICE: turn this off to do testing until figure out AWS database configuration'''
                # if os.path.isfile(history_file):
                #     aws_s3_upload_file(
                #         filename=history_file,
                #         s3_bucket=BUCKET_NAME,
                #         s3_filepath=S3_FILEPATH[key]
                #     )
                #     break
                # else:
                #     pass
            # Now create new file locally
            with open(filename, mode='w+') as data_file:
                csv_dict_writer = csv.DictWriter(data_file, fieldnames=data_header)
                csv_dict_writer.writeheader()
                csv_dict_writer.writerows(data)
                print('Wrote data for first time to:', filename)
        else:
            # Append to already existing file
            with open(filename, mode='a') as data_file:
                csv_dict_writer = csv.DictWriter(data_file, fieldnames=data_header)
                csv_dict_writer.writerows(data)
                print('Appended data to:', filename)
    except Exception as e:
        traceback.format_exc()
        print(type(e).__name__ + ': ' + str(e))

def aws_s3_upload_file(filename,s3_bucket,s3_filepath):
    '''
    Uploads locally stored file to AWS S3 bucket.
    Filename contains full filepath of the file locally.
    s3 bucket is the name of the target bucket and s3 filepath
    specifies the target location of the file in the bucket.\n
    filename: string\\
    s3_bucket: string\\
    s3_filepath: string\\
    returns: void
    '''
    try:
        s3_filename = s3_filepath + format(filename.split('/')[-1])
        s3.upload_file(filename, s3_bucket, s3_filename)
        logging.debug(filename, 'was uploaded to', s3_bucket)
        print(filename, 'was uploaded to  AWS S3 bucket:', s3_bucket)
    except ClientError as e:
        print(type(e).__name__ + ': ' + str(e))
        logging.error(e)
    except FileNotFoundError as e:
        print(type(e).__name__ + ': ' + str(e))
        logging.error(e)

def main():
    '''
    Manages sensors and data storage on device.\n
    return: void
    '''
    print('Running BevoBeacon2.0\n')
    i2c = createSensor()
    # Begin loop for sensor scans
    i = 1
    while True:
        print('*'*20 + ' LOOP %d '%i + '*'*20)
        try:
            print('Running SGP30 scan...')
            sgp30_scan(i2c)

            print('Running TSL2591 scan...')
            tsl2591_scan(i2c)

        except OSError as e:
                print('OSError for I/O on a sensor. sleeping 10 seconds...')
                time.sleep(10)
                continue

        # Data management
        print("Running data management...")
        data_mgmt()

        # Prepare for next loop
        delay = 60 #seconds
        print('Waiting', delay, 'seconds before rescanning...')
        #assert False
        time.sleep(delay)
        print('*'*20 + ' END ' + '*'*20)
        print('Rescanning...')
        i += 1

#********* EXECUTION START ************
main()
#************** END *******************
