
# ------------------------------------------------------------------------- #
# scd30_reader				       			       		    #
# ------------------------------------------------------------------------- #
# Description: This file is responsible for running the         #
# Sensirion SCD30 sensor. One user-created library is	    #
# imported to create the sensor instance. An infinite loop runs that takes #
# measurements from the sensor and stores them in a local csv file.        #	    #		
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
import math
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

# File Handling
# ------------------------------------------------------------------------- #
FILEPATH = {
	'scd30': '/home/pi/DATA/scd30/'
}
filename_writer = {
	'scd30': lambda date: FILEPATH['scd30'] + 'b' + beacon + '_' + date.strftime('%Y-%m-%d') + '.csv'
}

# Functions
# ------------------------------------------------------------------------- #
def scd30_scan():
	'''
	Measures the carbon dioxide concentration, temperature, and relative
	humidity in the room. Data are stored locally and to AWS S3 bucket.
	Returns a dictionary containing the carbon dioxide concentration in ppm,
	the temperature in degress Celsius, and the relative humidity as a 
	percent.
	'''

	try:
		tc, rh, co2 = scd30.takeMeasurement()
	except:
		print('Error reading from scd30')
		co2 = -100.0
		tc = -100.0
		rh = -100.0

	t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print("---------------------------------------")
	print("Time: "+str(t))
	print("\tCO2 (ppm): {0:.1f}".format(co2))
	print("\tT (C): {0:.1f}".format(tc))
	print("\tRH (%): {0:.1f}".format(rh))

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
	]
	data = [{
		'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
		'Temperature [C]': scd_data_old['TC'],
		'Relative Humidity': scd_data_old['RH'],
		'CO2': scd_data_old['CO2'],
	}]

	key = 'scd30'
	write_csv(
		key=key,
		date=timestamp,
		data_header=data_header,
		data=data
	)

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

def main():
	'''
	Manages sensors and data storage on device.\n
	return: void
	'''
	global scd_data_old

	print('Running IAQ Beacon - SCD30 ONLY\n')

	# Begin loop for sensor scans
	i = 1
	try:
		while True:
			print('*'*20 + ' LOOP %d '%i + '*'*20)
			scd_data_old = {'CO2':0,'TC':0,'RH':0}
			scd_count = 0
			for j in range(5):
				# SCD30 scan
				scd_data_new = scd30_scan()
				if scd_data_new['CO2'] != -100 and math.isnan(scd_data_new['CO2']) == False:
					if scd_data_new['TC'] > -20:
						scd_count += 1
						for x in scd_data_old:
							scd_data_old[x] += scd_data_new[x]

			for x in scd_data_old:
				try:
					scd_data_old[x] /= scd_count
				except ZeroDivisionError:
					scd_data_old[x] = 0

			print("---------------------------------------")
			print("Average:")
			print("---------------------------------------")
			print("\tCO2 (ppm): {0:.1f}".format(scd_data_old['CO2']))
			print("\tT (C): {0:.1f}".format(scd_data_old['TC']))
			print("\tRH (%): {0:.1f}".format(scd_data_old['RH']))
			print("---------------------------------------")
			
			# Data management
			print("Running data management...")
			data_mgmt()
	
			# Prepare for next loop
			delay = 20 #seconds
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
