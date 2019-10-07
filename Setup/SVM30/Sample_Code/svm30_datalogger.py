from datetime import datetime
import time
import busio
import adafruit_sgp30
import board
import csv

# Initialize the i2C bus object
i2c_bus = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Initialize the sgp30 sensor
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c_bus)

while True:
  time.sleep(4.99)
  # Read and output the data
  eCO2, TVOC = sgp30.iaq_measure()
  t = datetime.now()
  fields = [t,eCO2,TVOC]
  print("eCO2 = %d ppm \t TVOC = %d ppb" % (eCO2, TVOC))
  # Saving to CSV
  with open(r'Sample_Data_Collection/sgp30.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(fields)
