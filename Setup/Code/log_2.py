
# ------------------------------------------------------------------------- #
# log_2															   #
# ------------------------------------------------------------------------- #
# Description: The log_2 python file is responsible for running the         #
# Sensirion SPS30 and SCD30 sensors. Two user-created libraries are		   #
# imported to create the sensor instances. An infinite loop runs that takes #
# measurements from the sensors and stores it in a csv file	locally. Data	   #
# are pushed to an AWS S3 bucket periodically as well.					   #		
# -------------------------------------------------------------------------   #
# The University of Texas at Austin								         #
# Intelligent Environments Laboratory (IEL)								#
# Author: Hagen Fritz													#
#	With notable contributions from:									#
#	- Sepehr Bastami													#
#	- Dr. William Waites												#
#	- Kingsley Nweye													#
# Project: Indoor Environmental Quality and Sleep Quality					#
# Email: hagenfritz@utexas.edu											#
# ------------------------------------------------------------------------- #	

# General libraries
import time
import logging
import datetime
import csv
import os, signal
import sys
import struct
from subprocess import call

# Sensor-specific libraries
import crcmod
import pigpio
import sps30
import scd30

# AWS libraries
import boto3
from botocore.exceptions import ClientError

# AWS Setup
# ------------------------------------------------------------------------- #
# AWS setup for file upload to S3 bucket.
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
BUCKET_NAME = os.environ['BUCKET_NAME']

s3 = boto3.client(
    's3',
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY
)

S3_FILEPATH = {
    'sensirion': 'ECJ/test_beacon/DATA/sensirion/'
}
S3_CALL_FREQUENCY = datetime.timedelta(days=1)
S3_CALL_TIMESTAMP = {
    'sensirion': datetime.datetime.now()
}
# ------------------------------------------------------------------------- #

# File Handling
# ------------------------------------------------------------------------- #
FILEPATH = {
    'sensirion': '/home/pi/bevo_iaq/DATA/sensirion/'
}
filename_writer = {
    'sensirion': lambda date: FILEPATH['sensirion'] + date.strftime('%Y-%m-%d') + '_sensirion.csv'
}

# General Setup
# ------------------------------------------------------------------------- #
verbose = False

# Functions
# ------------------------------------------------------------------------- #
def sps30_scan():
    '''
    Measures different particulate matter counts and concentrations in the
    room. Data are stored locally and to AWS S3 bucket.
    Returns dictionary containing counts for 0.5, 1, 2.5 , 4, and 10 microns
    in diameter and concentrations for 1, 2.5, 4, and 10 microns in diameter.
    '''
    
    # Declare all global variables to be returned (n = count, c = concentration)
    global pm_n, pm_c

    # ----- #
    # Setup #
    # ----- #

    # Setting up communication
    PIGPIO_HOST = '127.0.0.1'
    I2C_SLAVE = 0x69
    I2C_BUS = 1

    # Checking to see if device is found
    deviceOnI2C = call("i2cdetect -y 1 0x69 0x69|grep '\--' -q", shell=True) # grep exits 0 if match found
    if deviceOnI2C:
        print("I2Cdetect found SPS30")
    else:
        print("SPS30 (0x69) not found on I2C bus")
        return False
      
    # Calls the exit_gracefully function when terminated from the command line
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    # Checking to see if pigpio is connected - if not, the command to run it is done via a call
    pi = pigpio.pi(PIGPIO_HOST)
    if not pi.connected:
        print("No connection to pigpio daemon at " + PIGPIO_HOST + ".")
        try:
            call("sudo pigpiod")
            print("Connection to pigpio daemon successful")
        except:
            return False
    else:
        print("Connection to pigpio daemon successful")

    # Not sure...
    try:
        pi.i2c_close(0)
    except:
        if sys.exc_value and str(sys.exc_value) != "'unknown handle'":
            print("Unknown error: ", sys.exc_type, ":", sys.exc_value)

    # Opens connection between the RPi and the sensor
    h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
    f_crc8 = crcmod.mkCrcFun(0x131, 0xFF, False, 0x00)

    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        sps30.exit_gracefully(False,False)

    # --------------- #
    # Data Collection #
    # --------------- #

    sps30.reset()
    time.sleep(0.1) # note: needed after reset

    sps30.initialize()

    ret = sps30.readDataReady()
    if ret == -1:
        print('resetting...',end='')
        sps30.bigReset()
        sps30.initialize()
        continue

    if ret == 0:
        time.sleep(0.1)
        continue

    data = sps30.readPMValues()
    
    # Count
    pm_n[0] = sps30.calcFloat(data[24:30])
    pm_n[1] = sps30.calcFloat(data[30:36])
    pm_n[2] = sps30.calcFloat(data[36:42])
    pm_n[3] = sps30.calcFloat(data[42:48])
    pm_n[4] = sps30.calcFloat(data[48:54])

    # Concentration
    pm_c[0] = sps30.calcFloat(data)
    pm_c[1] = sps30.calcFloat(data[6:12])
    pm_c[2] = sps30.calcFloat(data[12:18])
    pm_c[3] = sps30.calcFloat(data[18:24])

    return {'pm_n_0p5':pm_n[0],'pm_n_1':pm_n[1],'pm_n_2p5':pm_n[2],'pm_n_4':pm_n[3],'pm_n_10':pm_n[4],'pm_c_1':pm_c[0],'pm_c_2p5':pm_c[1],'pm_c_4':pm_c[2],'pm_c_10':pm_c[3]}

def scd30_scan(crc, pi, h, verbose):
    '''
    Measures the carbon dioxide concentration, temperature, and relative
    humidity in the room. Data are stored locally and to AWS S3 bucket.
    Returns a dictionary containing the carbon dioxide concentration in ppm,
    the temperature in degress Celsius, and the relative humidity as a 
    percent.
    '''

    # Declare all global variables to be returned
    global co2, tc, rh
    
    try:
        co2, tc, rh = scd30.calcCO2Values(pi,h,5,verbose)
        
    except:
        print('Problem opening connection to SCD30; saving dummy values')
        co2 = -100
        tc = -100
        rh = -100

    return {'CO2':co2,'TC':tc,'RH':rh}

def data_mgmt():
    '''
    Combines and stores sensors' data locally and remotely to AWS S3 bucket.\n
    return: void
    '''

    # Store combined sensor data locally and remotely
    timestamp = datetime.datetime.now()
    data_header = [
        'Timestamp',
        'Temperature [C]',
        'Relative Humidity',
        'CO2',
        'PM_N_0p5',
        'PM_N_1',
        'PM_N_2p5',
        'PM_N_4',
        'PM_N_10',
        'PM_C_1',
        'PM_C_2p5',
        'PM_C_4',
        'PM_C_10',
    ]
    data = [{
        'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'Temperature [C]': tc,
        'Relative Humidity': rh,
        'CO2': co2,
        'PM_N_0p5':pm_n[0],
        'PM_N_1':pm_n[1],
        'PM_N_2p5':pm_n[2],
        'PM_N_4':pm_n[3],
        'PM_N_10':pm_n[4],
        'PM_C_1':pm_c[0],
        'PM_C_2p5':pm_c[1],
        'PM_C_4':pm_c[2],
        'PM_C_10':pm_c[3],
    }]
    key = 'sensirion'
    write_csv(
        key=key,
        date=timestamp,
        data_header=data_header,
        data=data
    )

    # Control on S3 call frequency
    if timestamp - S3_CALL_TIMESTAMP[key] >= S3_CALL_FREQUENCY:
        aws_s3_upload_file(
            filename=filename_writer[key](date=timestamp),
            s3_bucket=BUCKET_NAME,
            s3_filepath=S3_FILEPATH[key]
        )
        S3_CALL_TIMESTAMP[key] = timestamp
    else:
        print('Upload to S3 bucket delayed.')

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
                if os.path.isfile(history_file):
                    aws_s3_upload_file(
                        filename=history_file,
                        s3_bucket=BUCKET_NAME,
                        s3_filepath=S3_FILEPATH[key]
                    )
                    break
                else:
                    pass
            # Now create new file locally
            with open(filename, mode='w') as data_file:
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
    print('Running IAQ Beacon\n')
    
    crc_sps, pi_sps, h_sps = sps30.setupSensor()
    print("SCD30 set up properly with")
    print("  handle:",h_sps)
    print("  pi:",pi_sps)
    
    crc_scd, pi_scd, h_scd = scd30.setupSensor()
    print("SCD30 set up properly with")
    print("  handle:",h_scd)
    print("  pi:",pi_scd)

    # Begin loop for sensor scans
    i = 1
    try:
        while True:
            print('*'*20 + ' LOOP %d '%i + '*'*20)
            try:
                # SPS30 scan
                print('Running SPS30 (pm) scan...')
                if not sps30_scan():
                    pm_n = [-1,-1,-1,-1,-1]
                    pm_c = [-1,-1,-1,-1]
    
                # SCD30 scan
                print('Running SCD30 (T,RH,CO2) scan...')
                scd30_scan(crc_scd, pi_scd, h_scd, verbose)
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
    except KeyboardInterrupt:
        print('User stopped operation')

# ------------------------------------------------------------------------- #

# Execution Start
# ------------------------------------------------------------------------- #
main()

# ------------------------------------------------------------------------- #