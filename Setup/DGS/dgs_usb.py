import os, sys
import serial
import time

ser = serial.Serial('/dev/ttyUSB0',9600,timeout=5)
while True:
	line = ser.readline()
	if len(line) == 0:
		exit(1)

	print(line)

	