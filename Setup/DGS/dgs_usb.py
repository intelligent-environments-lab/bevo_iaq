import os, sys
import serial
import time

ser = serial.Serial('/dev/ttyUSB0',baudrate=9600,bytesize=8,stopbits=1,timeout=5)
ser.open()
print(ser.isopen())
while True:
	print(ser.out_waiting)
	x = ser.read(8)

	print(x)

