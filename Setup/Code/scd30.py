#!/usr/bin/env python
# coding=utf-8
#
# --------------------------------------------------------------------------- #
# SCD30.py Module
# --------------------------------------------------------------------------- #
# Description: This module includes all the relevant functions to properly use
# the Sensirion SCD30 Sensor. To take a measurement, the following functions
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
import pprint
import struct
import sys
import os, signal
from subprocess import call
import crcmod # aptitude install python-crcmod
      
# Functions for Setting Up the Sensor
# --------------------------------------------------------------------------- #
      
def setupSensor():
    '''
    Initializes the sensor by trying to establish a connection with the sensor
    and returns the checksum object, device object, and sensor object.
    '''
    # Setting up communication
    PIGPIO_HOST = '127.0.0.1'
    I2C_SLAVE = 0x61
    I2C_BUS = 1

    # Checking to see if device is found
    deviceOnI2C = call("i2cdetect -y 1 0x61 0x61|grep '\--' -q", shell=True) # grep exits 0 if match found
    if deviceOnI2C:
        print("I2Cdetect found SCD30")

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
    
        # Opens connection between the RPi and the sensor with handle h
        h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
        f_crc8 = crcmod.mkCrcFun(0x131, 0xFF, False, 0x00)
        
        startMeasurement(f_crc8, pi, h)
      
        return f_crc8, pi, h

    else:
        print("SCD30 (0x61) not found on I2C bus")
        return False
    
def startMeasurement(f_crc8, pi, h):
    '''
    Starts the measurement sequence and sets the measurement interval to 2
    '''
    setMeasInterval(pi,h)
    # Add the command for continuous measurement?

def setMeasInterval(pi,h):
    '''
    Sets the measurement interval
    '''
    read_meas_result = readMeasInterval(pi,h)
    if read_meas_result == -1:
        eprint("setMeasInterval: command unsuccesful")
        exit(1)

    if read_meas_result != 2:
    # if not the specified interval, set it
        eprint("setMeasInterval: setting interval to",2)
        ret = i2cWrite([0x46, 0x00, 0x00, 0x02, 0xE3],pi,h)
        if ret == -1:
            exit(1)
        readMeasInterval(pi,h)
        
def readMeasInterval(pi,h):
    ret = i2cWrite([0x46, 0x00],pi,h)
    if ret == -1:
        return -1
    try:
        (count, data) = pi.i2c_read_device(h, 3)
    except:
        eprint("readMeasInterval: i2c_read failed")
        return -1

    if count == 3:
        if len(data) == 3:
            interval = int(data[0])*256 + int(data[1])
            return interval
        else:
            eprint("readMeasInterval: no array len 3 returned, instead " + str(len(data)) + "type: " + str(type(data)))
    else:
        eprint("readMeasInterval: read measurement interval didnt return 3B")
  
    return -1

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
        print("readDataReady: data found")
        return 1
    else:
        eprint("readDataReady: no data available")
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
        return False

    if count == n:
        return data
    else:
        eprint("error: read bytes didnt return " + str(n) + "B")
        return False
    
def readCO2Values(pi,h):
    '''
    Reads in the CO2, T, and RH values and returns the data.
    '''
    # READ MEASURED VALUES: 0x0300
    data = readFromAddr(0x03,0x00,18,pi,h)
    printHuman(data)
    return data

def calcCO2Values(pi,h,n):
    '''
    Takes an average of n measurements and returns the CO2 concetration,
    temperature in C, and relative humidity as a percent. The default
    measurement interval for the SCD30 is 2 seconds, meaning that the time for
    this code to execute should be approximately 2*n seconds. A loop counter
    ensures that if there is a problem communicating with the sensor, that we 
    don't get stuck in an infinite loop.
    '''
    co2s = []
    tcs = []
    rhs = []
    loop_count = 0
    max_loops = n*4
    while len(rhs) < n:
        if loop_count == max_loops:
            break
        ret = readDataReady(pi,h)
        if ret == 0:
            wait_time = 2
            print("  Waiting for",wait_time, "second(s) and checking again")
            print("  Loops left to check for data:",max_loops-loop_count)
            time.sleep(wait_time)
            
        elif ret == 1:
            data = readCO2Values(pi,h)
            co2s.append(calcFloat(data,[0,1,3,4]))
            tcs.append(calcFloat(data,[6,7,9,10]))
            rhs.append(calcFloat(data,[12,13,15,16]))
            
        else:
            eprint('resetting...',end='')
            pi, h = bigReset(pi,h)
            
        loop_count += 1
    
    return sum(co2s)/float(len(co2s)),sum(tcs)/float(len(tcs)),sum(rhs)/float(len(rhs))

# Helper Functions
# --------------------------------------------------------------------------- #

def eprint(*args, **kwargs):
    '''
    Error print function
    '''
    print(*args, file=sys.stderr, **kwargs)
  
    
def bigReset(pi,h_old):
    '''
    Inputs:
        -
    Performs a big reset i.e. closes the connection with the sensor and
    restarts it.
    '''
    eprint('Big reset...',end='')
    # Closing the connection and waiting for shutdown
    pi.i2c_close(h_old)
    # Re-initializing
    time.sleep(0.5)
    I2C_SLAVE = 0x61
    I2C_BUS = 1
    h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
    time.sleep(0.5)
    #reset(pi,h)
    #time.sleep(0.1) # note: needed after reset
    return pi, h

def calcFloat(sixBArray,pos):
    '''
    Inputs:
        - sixBArray: Array of two complement binary digits
        - pos: the indices where the data is held 
    Returns a float calculated using the six byte array
    '''
    struct_float = struct.pack('>BBBB', sixBArray[pos[0]], sixBArray[pos[1]], sixBArray[pos[2]], sixBArray[pos[3]])
    float_values = struct.unpack('>f', struct_float)
    first = float_values[0]
    return first

def printHuman(data):
    '''
    Inputs:
        - data: string of digits holding the measured data
    Prints the data to the terminal screen
    '''
    print("  CO2: %f" % calcFloat(data,[0,1,3,4]))
    print("  TC: %f" % calcFloat(data,[6,7,9,10]))
    print("  RH: %f" % calcFloat(data,[12,13,15,16]))
