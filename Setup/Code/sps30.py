#!/usr/bin/env python
# coding=utf-8
#
# --------------------------------------------------------------------------- #
# The University of Texas at Austin                        
# Intelligent Environments Laboratory (IEL)               
# Author: Hagen Fritz                       
# Project: Indoor Environmental Quality and Sleep Quality         
# Email: hagenfritz@utexas.edu                      
# --------------------------------------------------------------------------- # 

from __future__ import print_function

# This module uses the services of the C pigpio library. pigpio must be running on the Pi(s) whose GPIO are to be manipulated. 
# cmd ref: http://abyz.me.uk/rpi/pigpio/python.html#i2c_write_byte_data
import pigpio # aptitude install python-pigpio
import time
import struct
import sys
import crcmod # aptitude install python-crcmod
import os, signal
from subprocess import call

import pprint
from datetime import datetime
import csv

# --------- #
# Functions #
# --------- #

# Calculates checksum
def calcCRC(TwoBdataArray):
  byteData = ''.join(chr(x) for x in TwoBdataArray)
  return f_crc8(byteData)

# Reads the number of bytes from i2c device and if the number matches the input, returns the data as bytes
def readNBytes(n):
  '''
  Inputs:
    - n: integer specifying the number of bytes to read
  Returns the data from the device as bytes
  '''
  try:
    (count, data) = pi.i2c_read_device(h, n)
  except:
    print("error: i2c_read failed")
    return False

  if count == n:
    return data
  else:
    print("error: read bytes didnt return " + str(n) + "B")
    return False

# Write the data as bytes to the device
def i2cWrite(data):
  '''
  Input:
    - data: an array of bytes (integer-array)
  Returns True if able to write to the device or -1 if not
  '''
  try:
    pi.i2c_write_device(h, data)
  except Exception as e:
    print("error in i2c_write:")
    return -1
  return True

# Reads data given the i2c command and checks to see if the correct number of bytes are returned
def readFromAddr(LowB,HighB,nBytes):
  '''
  Inputs:
    - LowB: two left-hand values from command
    - HighB: two right-hand values from command
    - nBytes: number of bytes that should be returned
  Returns the data from the device or False otherwise
  '''
  for amount_tries in range(3):
    ret = i2cWrite([LowB, HighB])
    if ret != True:
      print("readFromAddr: write try unsuccessful, next")
      continue
    data = readNBytes(nBytes)
    if data:
      return data
    print("error in readFromAddr: " + hex(LowB) + hex(HighB) + " " + str(nBytes) + "B did return Nothing")
  print("readFromAddr: write tries(3) exceeded")
  return False

# Starts the measurement
def startMeasurement():
  '''
  Returns True is able to power up the device or False if not
  '''
  ret = -1
  for i in range(3):
    # START MEASUREMENT: 0x0010
    # READ MEASURED VALUES: 0x0300
    ret = i2cWrite([0x00, 0x10, 0x03, 0x00, calcCRC([0x03,0x00])])
    if ret == True:
      return True
    print('startMeasurement unsuccessful, next try')
    bigReset()
  print('startMeasurement unsuccessful, giving up')
  return False

# Shuts down the device by writing [0x01, 0x04] to the device
def stopMeasurement():
  # STOP MEASUREMENT: 0x0104
  i2cWrite([0x01, 0x04])

# Resets the device by writing [0xd3, 0x04] to the device
def reset():
  for i in range(5):
    ret = i2cWrite([0xd3, 0x04])
    if ret == True:
      return True
    print('reset unsuccessful, next try in', str(0.2 * i) + 's')
    time.sleep(0.2 * i)
  print('reset unsuccessful')
  return False

# Checks to see if there is data available to read in
def readDataReady():
  data = readFromAddr(0x02, 0x02,3)
  if data == False:
    print("readDataReady: command unsuccessful")
    return -1
  if data and data[1]:
    return 1
  else:
    return 0

# Calculates an integer given a six-byte array
def calcInteger(sixBArray):
  '''
  Inputs:
    - sixBArray: Array of two complement binary digits
  Returns an integer calculated using the six byte array
  '''
  integer = sixBArray[4] + (sixBArray[3] << 8) + (sixBArray[1] << 16) + (sixBArray[0] << 24)
  return integer

# Calculates a float value given a six-byte array
def calcFloat(sixBArray):
  '''
  Inputs:
    - sixBArray: Array of two complement binary digits
  Returns a float calculated using the six byte array
  '''
  struct_float = struct.pack('>BBBB', sixBArray[0], sixBArray[1], sixBArray[3], sixBArray[4])
  float_values = struct.unpack('>f', struct_float)
  first = float_values[0]
  return first

# Prints the data to the command line
def printHuman(data):
  '''
  Inputs:
    - data: string of digits holding the measured data
  Prints the data to the terminal screen
  '''
  print("pm0.5 count: %f" % calcFloat(data[24:30]))
  print("pm1   count: {0:.3f} concentration: {1:.3f}".format( calcFloat(data[30:36]), calcFloat(data) ) )
  print("pm2.5 count: {0:.3f} concentration: {1:.3f}".format( calcFloat(data[36:42]), calcFloat(data[6:12]) ) )
  print("pm4   count: {0:.3f} concentration: {1:.3f}".format( calcFloat(data[42:48]), calcFloat(data[12:18]) ) )
  print("pm10  count: {0:.3f} concentration: {1:.3f}".format( calcFloat(data[48:54]), calcFloat(data[18:24]) ) )
  print("pm_typ: %f" % calcFloat(data[54:60]))

# Reads data from the device and outputs it to the command line
def readPMValues():
  # READ MEASURED VALUES: 0x0300
  data = readFromAddr(0x03,0x00,59)
  printHuman(data)
  return data

# Initializes the measurement
def initialize():
  startMeasurement()
  time.sleep(0.9)

# Big reset
def bigReset():
  global h
  print('resetting...',end='')
  pi.i2c_close(h)
  time.sleep(0.5)
  h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
  time.sleep(0.5)
  reset()
  time.sleep(0.1) # note: needed after reset
