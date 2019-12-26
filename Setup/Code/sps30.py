#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2018 UnravelTEC
# Michael Maier <michael.maier+github@unraveltec.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# If you want to relicense this code under another license, please contact info+github@unraveltec.com.

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

def takeMeasurement():
  '''
  Gets some values
  '''

  global pi
  global h
  global f_crc8

  pm_n = [-100.0,-100.-100,-100.0,-100.0,-100.0]
  pm_c = [-100.0,-100.0,-100.0,-100.0]
  # --------- #
  # Functions #
  # --------- #
    
  # Error print function
  def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    
  # Exits the program
  def exit_gracefully(a,b):
    print("\nexiting...")
    stopMeasurement()
    pi.i2c_close(h)
    exit(0)

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
      eprint("error: i2c_read failed")

    if count == n:
      return data
    else:
      eprint("error: read bytes didnt return " + str(n) + "B")
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
      pprint.pprint(e)
      eprint("error in i2c_write:", e.__doc__ + ":",  e.value)
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
        eprint("readFromAddr: write try unsuccessful, next")
        continue
      data = readNBytes(nBytes)
      if data:
        return data
      eprint("error in readFromAddr: " + hex(LowB) + hex(HighB) + " " + str(nBytes) + "B did return Nothing")
    eprint("readFromAddr: write tries(3) exceeded")
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
      eprint('startMeasurement unsuccessful, next try')
      bigReset()
    eprint('startMeasurement unsuccessful, giving up')
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
      eprint('reset unsuccessful, next try in', str(0.2 * i) + 's')
      time.sleep(0.2 * i)
    eprint('reset unsuccessful')
    return False

  # Checks to see if there is data available to read in
  def readDataReady():
    data = readFromAddr(0x02, 0x02,3)
    if data == False:
      eprint("readDataReady: command unsuccessful")
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
    print("Concentration (ug/m3)")
    print("---------------------------------------")
    print("PM1: {0:.3f}\tPM2.5: {0:.3f}\tPM4: {0:.3f}\tPM10: {0:.3f}".format(calcFloat(data), calcFloat(data[6:12]), calcFloat(data[12:18]), calcFloat(data[18:24])))
    print("Count (#/L)")
    print("---------------------------------------")
    print("PM0.5 count: {0:.3f}".format(calcFloat(data[24:30])))
    print("PM1   count: {0:.3f}".format(calcFloat(data[30:36])))
    print("PM2.5 count: {0:.3f}".format(calcFloat(data[36:42])))
    print("PM4   count: {0:.3f}".format(calcFloat(data[42:48])))
    print("PM10  count: {0:.3f}".format(calcFloat(data[48:54])))
    print("---------------------------------------")
    print("Typical Size: {0:.3f}".format(calcFloat(data[54:60])))
    print("---------------------------------------")

  # Reads data from the device and outputs it to the command line
  def readPMValues():
    # READ MEASURED VALUES: 0x0300
    data = readFromAddr(0x03,0x00,59)
    if data != False:
      printHuman(data)
    return data

  # Initializes the measurement
  def initialize():
    startMeasurement()
    time.sleep(0.9)

  # Big reset
  def bigReset():
    global h
    eprint('resetting...',end='')
    pi.i2c_close(h)
    time.sleep(0.5)
    h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
    time.sleep(0.5)
    reset()
    time.sleep(0.1) # note: needed after reset

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
    
  # Calls the exit_gracefully function when terminated from the command line
  signal.signal(signal.SIGINT, exit_gracefully)
  signal.signal(signal.SIGTERM, exit_gracefully)

  # Checking to see if pigpio is connected - if not, the command to run it is done via a call
  pi = pigpio.pi(PIGPIO_HOST)
  if not pi.connected:
    eprint("No connection to pigpio daemon at " + PIGPIO_HOST + ".")
    try:
      call("sudo pigpiod")
      print("Connection to pigpio daemon successful")
    except:
      exit(1)
  else:
    print("Connection to pigpio daemon successful")

  # Not sure...
  try:
    pi.i2c_close(0)
  except:
    if sys.exc_value and str(sys.exc_value) != "'unknown handle'":
      eprint("Unknown error: ", sys.exc_type, ":", sys.exc_value)

  # Opens connection between the RPi and the sensor
  h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
  f_crc8 = crcmod.mkCrcFun(0x131, 0xFF, False, 0x00)

  if len(sys.argv) > 1 and sys.argv[1] == "stop":
    exit_gracefully(False,False)

  # --------------- #
  # Data Collection #
  # --------------- #

  reset()
  time.sleep(0.1) # note: needed after reset

  initialize()

  ret = readDataReady()
  if ret == -1:
    eprint('resetting...',end='')
    bigReset()
    initialize()

  if ret == 0:
    time.sleep(0.1)

  data = readPMValues()

  pm_typical = calcFloat(data[54:60])
  if pm_typical > 0:
    # Count 
    pm_n[0] += calcFloat(data[24:30])
    pm_n[1] += calcFloat(data[30:36])
    pm_n[2] += calcFloat(data[36:42])
    pm_n[3] += calcFloat(data[42:48])
    pm_n[4] += calcFloat(data[48:54])

    # Concentration
    pm_c[0] += calcFloat(data)
    pm_c[1] += calcFloat(data[6:12])
    pm_c[2] += calcFloat(data[12:18])
    pm_c[3] += calcFloat(data[18:24])

  pi.i2c_close(h)
  pi.stop()

  return pm_n, pm_c
