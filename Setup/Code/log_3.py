# **********************************************************************
# The University of Texas at Austin                                    *
# Intelligent Environments Laboratory (IEL)                            *
# Author: Hagen Fritz and Dung Le		                       *
# Project:                                                             *
# Email: hoangdung.le@utexas.edu                                       *
# **********************************************************************

import time
import math
import csv
import datetime
import os
import traceback
import logging
import smtplib, ssl
import binascii

# Import sensor-specific libraries
import serial
import dgs
import adafruit_sgp30
import adafruit_tsl2591
from board import SCL, SDA
from busio import I2C

# AWS libraries
import boto3
from botocore.exceptions import ClientError

beacon = '00'
 
# Verbose Global Variable
verbose = True

# Create I2C Object for sensors
# Also sets setup mode for GPIO to BCM
def createSensor():
	i2c = I2C(SCL, SDA)
	return i2c

#*****************************************
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
	'adafruit':'WCWH/spring2020/adafruit/'
}
S3_CALL_FREQUENCY = datetime.timedelta(days=7)
S3_CALL_TIMESTAMP = {
	'adafruit': datetime.datetime.now()
}
#*****************************************
# File handling
FILEPATH = {
	'adafruit':'/home/pi/DATA/adafruit/'
}
filename_writer = {
	'adafruit': lambda date: FILEPATH['adafruit'] + 'b' + beacon + '_' + date.strftime('%Y-%m-%d') + '.csv'
}
#*****************************************
# import functions for each of the sensors
def sgp30_scan(sgp30):
	# Declare all global variables for use outside the functions
	global eCO2, TVOC
	try:
		# Retrieve sensor scan data
		eCO2, TVOC = sgp30.iaq_measure()
	except:
		print('Error reading from SGP30')
		eCO2 = -100
		TVOC = -100

	# Outputting
	if verbose:
		print("-------------------------")
		print("TVOC (ppb):\t"+str(TVOC))
		print("eCO2 (ppm):\t"+str(eCO2))
		print("-------------------------")
	# Return data
	data = {'TVOC': TVOC, 'eCO2': eCO2}
	return data

def tsl2591_scan(tsl):
	# Declare all global variables for use outside the functions
	global lux, visible, infrared
	try:
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
	except:
		print('Error reading from TSL2591')
		lux = -100
		visible = -100
		infrared = -100
	# Outputting
	if verbose:
		print("-------------------------")
		print("Visible (?):\t"+str(visible))
		print("Infrared (?):\t"+str(infrared))
		print("Bright (lux):\t"+str(lux))
		print("-------------------------")
	# Return data
	data = {'Visible': visible, 'Infrared': infrared, 'Lux': lux}
	return data

def NO2_scan():
	'''
	Using serial connection, reads in values for T, RH, and NO2 concentration
	'''
	global no2, t0, rh0

	try:
		no2, t0, rh0 = dgs.takeMeasurement('/dev/ttyUSB0')
	except:
		print('Error reading from NO2 sensor')
		co = -100
		t0 = -100
		rh0 = -100

	data = {'NO2':no2,'T_NO2':t0,'RH_NO2':rh0}
	return data

def CO_scan():
	'''
	Using serial connection, reads in values for T, RH, and CO concentration
	'''
	global co, t1, rh1
	try:
		co, t1, rh1 = dgs.takeMeasurement('/dev/ttyUSB1')
	except:
		print('Error reading from CO sensor')
		co = -100
		t1 = -100
		rh1 = -100

	data = {'CO':co,'T_CO':t1,'RH_CO':rh1}
	return data

def data_mgmt():
	# Store adafruit sensor data locally and remotely
	timestamp = datetime.datetime.now()
	data_header = [
		'Timestamp',
		'TVOC',
		'eCO2',
		'Lux',
		'Visible',
		'Infrared',
		'NO2',
		'T_NO2',
		'RH_NO2',
		'CO',
		'T_CO',
		'RH_CO'
	]
	data = [{
		'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
		'TVOC': sgp_data_old['TVOC'],
		'eCO2': sgp_data_old['eCO2'],
		'Lux': tsl_data_old['Lux'],
		'Visible': tsl_data_old['Visible'],
		'Infrared': tsl_data_old['Infrared'],
		'NO2': no2_data_old['NO2'],
		'T_NO2': no2_data_old['T_NO2'],
		'RH_NO2': no2_data_old['RH_NO2'],
		'CO': co_data_old['CO'],
		'T_CO': co_data_old['T_CO'],
		'RH_CO': co_data_old['RH_CO']
	}]
	key = 'adafruit'
	write_csv(
		key=key,
		date=timestamp,
		data_header=data_header,
		data=data
	)

	# Control on S3 call frequency
	if timestamp - S3_CALL_TIMESTAMP[key] >= S3_CALL_FREQUENCY:
	#	aws_s3_upload_file(
	#		filename=filename_writer[key](date=timestamp),
	#		s3_bucket=BUCKET_NAME,
	#		s3_filepath=S3_FILEPATH[key]
	#	)
	#	S3_CALL_TIMESTAMP[key] = timestamp
		pass
	else:
		if verbose:
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
			#history_limit = 10 # Days
			#for i in range(1,history_limit):
			#	history_date = date - datetime.timedelta(days=i)
			#	history_file = filename_writer[key](date=history_date)
			#	if os.path.isfile(history_file):
			#		aws_s3_upload_file(
			#			filename=history_file,
			#			s3_bucket=BUCKET_NAME,
			#			s3_filepath=S3_FILEPATH[key]
			#		)
			#		break
			#	else:
			#		pass
			# Now create new file locally
			with open(filename, mode='w+') as data_file:
				csv_dict_writer = csv.DictWriter(data_file, fieldnames=data_header)
				csv_dict_writer.writeheader()
				csv_dict_writer.writerows(data)
				if verbose:
					print('Wrote data for first time to:', filename)
		else:
			# Append to already existing file
			with open(filename, mode='a') as data_file:
				csv_dict_writer = csv.DictWriter(data_file, fieldnames=data_header)
				csv_dict_writer.writerows(data)
				if verbose:
					print('Appended data to:', filename)
	except Exception as e:
		traceback.format_exc()
		if verbose:
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
		if verbose:
			print(filename, 'was uploaded to  AWS S3 bucket:', s3_bucket)
	except ClientError as e:
		if verbose:
			print(type(e).__name__ + ': ' + str(e))
		logging.error(e)
	except FileNotFoundError as e:
		if verbose:
			print(type(e).__name__ + ': ' + str(e))
		logging.error(e)

def main():
	'''
	Manages sensors and data storage on device.\n
	return: void
	'''
	print('Running BevoBeacon2.0\n')
	i2c = createSensor()
	# Setting up sgp30
	try:
		sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
		sgp30.iaq_init()
	except ValueError:
		print("No device")

	# Instantiate tsl object
	try:
		tsl = adafruit_tsl2591.TSL2591(i2c)
	except Exception as inst:
		print(inst)

	global sgp_data_old, tsl_data_old, no2_data_old, co_data_old
	# Begin loop for sensor scans
	i = 1
	while True:
		print('*'*20 + ' LOOP %d '%i + '*'*20)
		sgp_data_old = {'TVOC': 0, 'eCO2': 0}
		sgp_count = 0
		tsl_data_old = {'Visible': 0, 'Infrared': 0, 'Lux': 0}
		tsl_count = 0
		no2_data_old = {'NO2':0,'T_NO2':0,'RH_NO2':0}
		no2_count = 0
		co_data_old = {'CO':0,'T_CO':0,'RH_CO':0}
		co_count = 0
		for j in range(5):
			#print('Running SGP30 scan...')
			try:
				sgp_data_new = sgp30_scan(sgp30)
				if sgp_data_new['TVOC'] != -100 and math.isnan(sgp_data_new['TVOC']) == False:
					sgp_count += 1
					for x in sgp_data_old:
						sgp_data_old[x] += sgp_data_new[x]
			except Exception as inst:
				print(inst)
			
			#print('Running TSL2591 scan...')
			try:
				tsl_data_new = tsl2591_scan(tsl)
				if tsl_data_new['Lux'] != -100 and math.isnan(tsl_data_new['Lux']) == False:
					tsl_count += 1
					for x in tsl_data_old:
						tsl_data_old[x] += tsl_data_new[x]
			except Exception as inst:
				print(inst)

			#print('Running Nitrogen Dioxide scan...')
			no2_data_new = NO2_scan()
			if int(no2_data_new['NO2']) != -100 and math.isnan(int(no2_data_new['NO2'])) == False:
				no2_count += 1
				for x in no2_data_old:
					no2_data_old[x] += int(no2_data_new[x])

			#print('Running Carbon Monoxide scan...')
			co_data_new = CO_scan()
			if int(co_data_new['CO']) != -100 and math.isnan(int(co_data_new['CO'])) == False:
				co_count += 1
				for x in co_data_old:
					co_data_old[x] += int(co_data_new[x])

		for x in sgp_data_old:
			try:
				sgp_data_old[x] /= sgp_count
			except ZeroDivisionError:
				sgp_data_old[x] = -100

		for x in tsl_data_old:
			try:
				tsl_data_old[x] /= tsl_count
			except ZeroDivisionError:
				tsl_data_old[x] = -100

		for x in no2_data_old:
			try:
				no2_data_old[x] /= no2_count
			except ZeroDivisionError:
				no2_data_old[x] = -100

		for x in co_data_old:
			try:
				co_data_old[x] /= co_count
			except ZeroDivisionError:
				co_data_old[x] = -100

		print("---------------------------------------")
		print("Average Values")
		print("---------------------------------------")
		print("TVOC (ug/m3): {0:.3f}".format(sgp_data_old['TVOC']))
		print("Light (lux): {0:.3f}".format(tsl_data_old['Lux']))
		print("NO2 (ppb): {0:.3f}".format(no2_data_old['NO2']))
		print("CO (ppb): {0:.3f}".format(co_data_old['CO']))
		print("---------------------------------------")

		# Data management
		print("Running data management...")
		data_mgmt()

		# Prepare for next loop
		delay = 50 #seconds
		print('Waiting', delay, 'seconds before rescanning...')
		#assert False
		time.sleep(delay)
		print('*'*20 + ' END ' + '*'*20)
		print('Rescanning...')
		i += 1

#********* EXECUTION START ************
main()
#************** END *******************
