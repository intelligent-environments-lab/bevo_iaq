import os, sys
import serial
import time

ser = serial.Serial('/dev/ttyUSB0',9600,timeout=5)
print(ser.name)
while True:
	x = ser.read()

	print(x)

