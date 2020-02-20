
# ------------------------------------------------------------------------- #
# log_2				       			       		    #
# ------------------------------------------------------------------------- #
# Description: The log_2 python file is responsible for running the         #
# Sensirion SPS30 and SCD30 sensors. Two user-created libraries are	    #
# imported to create the sensor instances. An infinite loop runs that takes #
# measurements from the sensors and stores it in a csv file locally.        #
# Data are pushed to an AWS S3 bucket periodically as well.		    #		
# ------------------------------------------------------------------------- #
# The University of Texas at Austin				            #
# Intelligent Environments Laboratory (IEL)				    #
# Author: Hagen Fritz							    #
#	With notable contributions from:			  	    #
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
import smtplib, ssl
from subprocess import call

# Sensor-specific libraries
import crcmod
import pigpio
import sps30
import scd30

# AWS libraries
import boto3
from botocore.exceptions import ClientError

beacon = '00'

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
	'sensirion': 'WCWH/spring2020/sensirion/'
}
S3_CALL_FREQUENCY = datetime.timedelta(days=7)
S3_CALL_TIMESTAMP = {
	'sensirion': datetime.datetime.now()
}
# ------------------------------------------------------------------------- #

# File Handling
# ------------------------------------------------------------------------- #
FILEPATH = {
	'sensirion': '/home/pi/DATA/sensirion/'
}
filename_writer = {
	'sensirion': lambda date: FILEPATH['sensirion'] + 'b' + beacon + '_' + date.strftime('%Y-%m-%d') + '.csv'
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

	pm_n, pm_c = sps30.takeMeasurement()

	print("---------------------------------------")
	print("Concentration (ug/m3)")
	print("---------------------------------------")
	print("PM1: {0:.3f}".format(pm_c[0]))
	print("PM2.5: {0:.3f}".format(pm_c[1]))
	print("PM4: {0:.3f}".format(pm_c[2]))
	print("PM10: {0:.3f}".format(pm_c[3]))
	print("---------------------------------------")
	print("Count (#/L)")
	print("---------------------------------------")
	print("PM0.5 count: {0:.3f}".format(pm_n[0]))
	print("PM1   count: {0:.3f}".format(pm_n[1]))
	print("PM2.5 count: {0:.3f}".format(pm_n[2]))
	print("PM4   count: {0:.3f}".format(pm_n[3]))
	print("PM10  count: {0:.3f}".format(pm_n[4]))
	print("---------------------------------------")

	return {'pm_n_0p5':pm_n[0],'pm_n_1':pm_n[1],'pm_n_2p5':pm_n[2],'pm_n_4':pm_n[3],'pm_n_10':pm_n[4],'pm_c_1':pm_c[0],'pm_c_2p5':pm_c[1],'pm_c_4':pm_c[2],'pm_c_10':pm_c[3]}

def scd30_scan():
	'''
	Measures the carbon dioxide concentration, temperature, and relative
	humidity in the room. Data are stored locally and to AWS S3 bucket.
	Returns a dictionary containing the carbon dioxide concentration in ppm,
	the temperature in degress Celsius, and the relative humidity as a 
	percent.
	'''

	# Declare all global variables to be returned
	global co2, tc, rh

	tc, rh, co2 = scd30.takeMeasurement()

	print("---------------------------------------")
	print("Environmental Variables")
	print("---------------------------------------")
	print("CO2 (ppm): {0:.1f}".format(co2))
	print("T (C): {0:.1f}".format(t))
	print("RH (%): {0:.1f}".format(rh))
	print("---------------------------------------")

	return {'CO2':co2,'TC':tc,'RH':rh}

def error_email(error_message):
	'''
	DOES NOT WORK WITH PYTHON2
	'''
	port = 465  # For SSL
	smtp_server = "smtp.gmail.com"
	sender_email = "IEL.Beacon.Manager@gmail.com"  # Enter your address
	receiver_email = "IEL.Beacon.Manager@gmail.com"  # Enter receiver address
	password = "ZoltanIEL2019"
	message = """\
	Subject: Sensor is down

	{error_message}"""

	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email, message.format(error_message=error_message))

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

	# Begin loop for sensor scans
	i = 1
	try:
		while True:
			print('*'*20 + ' LOOP %d '%i + '*'*20)
			sps_data_old = {'pm_n_0p5':0,'pm_n_1':0,'pm_n_2p5':0,'pm_n_4':0,'pm_n_10':0,'pm_c_1':0,'pm_c_2p5':0,'pm_c_4':0,'pm_c_10':0}
			sps_count = 0
			scd_data_old = {'CO2':0,'TC':0,'RH':0}
			scd_count = 0
			for i in range(5):
				try:
					# SPS30 scan
					sps_data_new = sps30_scan()
					if sps_data_new['pm_n_10'] != -100:
						sps_count += 1
						for x in sps_data_old:
							sps_data_old[x] += sps_data_new[x]
		
					# SCD30 scan
					scd_data_new = scd30_scan()
					if scd_data_new['CO2'] != -100:
						scd_count += 1
						for x in scd_data_old:
							scd_data_old[x] += scd_data_new[x]

				except OSError as e:
					print('OSError for I/O on a sensor.')

			for x in sps_data_old:
				sps_data_old[x] /= sps_count

			for x in scd_data_old:
				scd_data_old[x] /= scd_count

			print("---------------------------------------")
			print("Average PM Concentration (ug/m3)")
			print("---------------------------------------")
			print("PM1: {0:.3f}".format(sps_data_old['pm_c_1']))
			print("PM2.5: {0:.3f}".format(sps_data_old['pm_c_2p5']))
			print("PM4: {0:.3f}".format(sps_data_old['pm_c_4']))
			print("PM10: {0:.3f}".format(sps_data_old['pm_c_10']))
			print("---------------------------------------")
			print("Average PM Count (#/L)")
			print("---------------------------------------")
			print("PM0.5 count: {0:.3f}".format(sps_data_old['pm_n_0p5']))
			print("PM1   count: {0:.3f}".format(sps_data_old['pm_n_1']))
			print("PM2.5 count: {0:.3f}".format(sps_data_old['pm_n_2p5']))
			print("PM4   count: {0:.3f}".format(sps_data_old['pm_n_4']))
			print("PM10  count: {0:.3f}".format(sps_data_old['pm_n_10']))
			print("---------------------------------------")

			print("---------------------------------------")
			print("Average Environmental Variables")
			print("---------------------------------------")
			print("CO2 (ppm): {0:.1f}".format(scd_data_old['CO2']))
			print("T (C): {0:.1f}".format(scd_data_old['TC']))
			print("RH (%): {0:.1f}".format(scd_data_old['RH']))
			print("---------------------------------------")
			
			# Data management
			print("Running data management...")
			data_mgmt()
	
			# Prepare for next loop
			delay = 56 #seconds
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
