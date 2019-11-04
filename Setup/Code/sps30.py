#!/usr/bin/env python
# coding=utf-8
#
# --------------------------------------------------------------------------- #
# SPS30.py Module
# --------------------------------------------------------------------------- #
# Description: This module includes all the relevant functions to properly use
# the Sensirion SPS30 Sensor. To take a measurement, the following functions
# are run in this order:
#
#   Start-Up Process:
#   - setupSensor()
#   - initialize()
#   - startMeasurement()
#   - i2cWrite()
#
#   Measurement Process:
#   - readDataReady()
#       - readFromAddr()
#           - i2cWrite()
#       - readNBytes()
#   - ReadPMValues
#       - readFromAddr()
#       - readNBytes()
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

# Functions for Setting Up the Sensor
# --------------------------------------------------------------------------- #
  
def setupSensor():
    '''
    Initializes the sensor by trying to establish a connection with the sensor
    and returns the checksum object, device object, and sensor object.
    '''
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
        exit(1)

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

    try:
        pi.i2c_close(0)
    except:
        print("Could not close connection on handle 0")

    # Opens connection between the RPi and the sensor
    h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
    f_crc8 = crcmod.mkCrcFun(0x131, 0xFF, False, 0x00)
  
    return f_crc8, pi, h

def startMeasurement(f_crc8,pi,h):
    '''
    Returns True if able to power up the device and connect to the sensor
    or False if not
    '''
    for i in range(2):
        # START MEASUREMENT: 0x0010
        # READ MEASURED VALUES: 0x0300
        ret = i2cWrite([0x00, 0x10, 0x03, 0x00, calcCRC([0x03,0x00],f_crc8)],pi,h)
        if ret == True:
            return True
        else:
            eprint('startMeasurement unsuccessful, next try')
            pi, h = bigReset(pi,h)
            
    eprint('startMeasurement unsuccessful, giving up')
    return False

def i2cWrite(data,pi,h):
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

# Measurement Recording Functions
# --------------------------------------------------------------------------- #
    
def readDataReady(pi,h):
    '''
    Checks to see if there is data available to read in
    Returns -1 if no data or 1 if there is
    '''
    data = readFromAddr(0x02, 0x02,3,pi,h)
    if data == False:
        eprint("readDataReady: command unsuccessful")
        return -1
    if data and data[1]:
        return 1
    else:
        return 0
    
def readFromAddr(LowB,HighB,nBytes,pi,h):
    '''
    Inputs:
        - LowB: two left-hand values from command
        - HighB: two right-hand values from command
        - nBytes: number of bytes that should be returned
    Returns data from the device based on the byte values or False otherwise
    '''
    for amount_tries in range(3):
        ret = i2cWrite([LowB, HighB],pi,h)
        if ret != True:
            eprint("readFromAddr: write try unsuccessful, next")
            continue
        data = readNBytes(nBytes,pi,h)
        if data:
            return data
        eprint("error in readFromAddr: " + hex(LowB) + hex(HighB) + " " + str(nBytes) + "B did return Nothing")
    eprint("readFromAddr: write tries(3) exceeded")
    return False

def readNBytes(n,pi,h):
    '''
    Inputs:
        - n: integer specifying the number of bytes to read
    Returns the data from the device as bytes
    '''
    try:
        (count, data) = pi.i2c_read_device(h, n)
    except:
        eprint("error: i2c_read failed")
        exit(1)

    if count == n:
        return data
    else:
        eprint("error: read bytes didnt return " + str(n) + "B")
        return False
    
def readPMValues(pi,h):
    '''
    Reads in the Pm values and returns the data.
    '''
    # READ MEASURED VALUES: 0x0300
    data = readFromAddr(0x03,0x00,59,pi,h)
    #printHuman(data)
    return data

def calcPMValues(pi,h,n):
    '''
    
    '''
    pm_n = [0,0,0,0,0]
    pm_c = [0,0,0,0]
    sum_count = 0
    loop_count = 0
    max_loops = n*4
    while sum_count < n:
        if loop_count == max_loops:
            break
        ret = readDataReady(pi,h)
        if ret == 0:
            wait_time = 2
            print("  Waiting for",wait_time, "second(s) and checking again")
            print("  Loops left to check for data:",max_loops-loop_count)
            time.sleep(wait_time)
            
        elif ret == 1:
            sum_count += 1
            data = readPMValues(pi,h)
            # Number
            pm_n[0] += calcFloat(data[24:30])
            pm_n[1] += calcFloat(data[30:36])
            pm_n[2] += calcFloat(data[36:42])
            pm_n[3] += calcFloat(data[42:48])
            pm_n[4] += calcFloat(data[48:54])
            # Concentration
            pm_c[0] += calcFloat(data[0:6])
            pm_c[1] += calcFloat(data[6:12])
            pm_c[2] += calcFloat(data[12:18])
            pm_c[3] += calcFloat(data[18:24])
            
        else:
            eprint('resetting...',end='')
            pi, h = bigReset(pi,h)
            
        loop_count += 1
        
    for i in range(len(pm_n)):
        pm_n[i] = pm_n[i]/5
    
    for i in range(len(pm_c)):
        pm_c[i] = pm_c[i]/5
        
    return pm_n, pm_c

# Helper Functions
# --------------------------------------------------------------------------- #

def eprint(*args, **kwargs):
    '''
    Error print function
    '''
    print(*args, file=sys.stderr, **kwargs)
  
def exit_gracefully(a,b,pi,h):
    '''
    Exits the program gracefully upon user command
    '''
    print("\nexiting...")
    stopMeasurement(pi,h)
    pi.i2c_close(h)
    exit(0)
    
def reset(pi,h):
    '''
    Tries to reset the device by writing [0xd3, 0x04] (reset command) to the it
    '''
    for i in range(2):
        ret = i2cWrite([0xd3, 0x04],pi,h)
        if ret == True:
            return True
        eprint('reset unsuccessful, next try in', str(0.2 * i) + 's')
        time.sleep(0.2 * i)
    eprint('reset unsuccessful')
    return False

def bigReset(pi,h_old):
    '''
    Inputs:
        -
    Performs a big reset i.e. closes the connection with the sensor and
    restarts it.
    '''
    eprint('resetting...',end='')
    # Closing the connection and waiting for shutdown
    pi.i2c_close(h_old)
    # Re-initializing
    time.sleep(0.5)
    I2C_SLAVE = 0x69
    I2C_BUS = 1
    h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
    time.sleep(0.5)
    reset(pi,h)
    time.sleep(0.1) # note: needed after reset
    return pi, h

def stopMeasurement(pi,h):
    '''
    Shuts down the device by writing [0x01, 0x04] to it
    '''
    # STOP MEASUREMENT: 0x0104
    i2cWrite([0x01, 0x04],pi,h)
    
def calcCRC(TwoBdataArray,f_crc8):
    '''
    Calculates checksum and returns the value
    '''
    byteData = ''.join(chr(x) for x in TwoBdataArray)
    print(byteData)
    return f_crc8(byteData)

def calcInteger(sixBArray):
    '''
    Inputs:
        - sixBArray: Array of two complement binary digits
    Returns an integer calculated using the six byte array
    '''
    integer = sixBArray[4] + (sixBArray[3] << 8) + (sixBArray[1] << 16) + (sixBArray[0] << 24)
    return integer

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

def printHuman(n,c):
    '''
    
    '''
    print("  pm0.5 count: %f" % n[0])
    print("  pm1   count: {0:.3f} concentration: {1:.3f}".format( n[1], c[0] ))
    print("  pm2.5 count: {0:.3f} concentration: {1:.3f}".format( n[2], c[1] ) )
    print("  pm4   count: {0:.3f} concentration: {1:.3f}".format( n[3], c[2] ) )
    print("  pm10  count: {0:.3f} concentration: {1:.3f}".format( n[4], c[3] ) )
    
def printHuman_old(data):
    '''
    Inputs:
        - data: string of digits holding the measured data
    Prints the data to the terminal screen
    '''
    print("  pm0.5 count: %f" % calcFloat(data[24:30]))
    print("  pm1   count: {0:.3f} concentration: {1:.3f}".format( calcFloat(data[30:36]), calcFloat(data) ) )
    print("  pm2.5 count: {0:.3f} concentration: {1:.3f}".format( calcFloat(data[36:42]), calcFloat(data[6:12]) ) )
    print("  pm4   count: {0:.3f} concentration: {1:.3f}".format( calcFloat(data[42:48]), calcFloat(data[12:18]) ) )
    print("  pm10  count: {0:.3f} concentration: {1:.3f}".format( calcFloat(data[48:54]), calcFloat(data[18:24]) ) )
    print("  pm_typ: %f" % calcFloat(data[54:60]))