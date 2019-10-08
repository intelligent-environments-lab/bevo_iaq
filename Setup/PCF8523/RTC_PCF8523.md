
# Installation Instructions and Documentation for the Adafruit PCF8523 Real-Time-Clock Sensor
This page contains all the pertinent information to setup and run the Adafruit PCF8523 Real-Time-Clock (RTC). For more information see this [webpage](https://learn.adafruit.com/adafruit-pcf8523-real-time-clock/overview) on the sensor. 

## PCF8523 RTC
![RTC](https://www.robotics.org.za/image/cache/catalog/adafruit/AF3295/AF3295-000-650x350.jpg)

## Hardware Connection for the RTC
The RTC requires a connection for the 4 of the 5 pins on the sensor. From left to right, the pins correspond to:
1. **GND**: Ground pin
2. **Vcc**: Power pin
5. **SDA**: I2C data pin
4. **SCL**: I2C clock pin
3. **SQW**: Square-Wave output (not used in this setup)

The acronyms are described in the image above. This document and setup is for I2C communication which means we will be using the SDA/SCL pins on the RPi to set up the connection. The RPi pinout is shown below for reference:

![RPI_Pinout](https://docs.microsoft.com/en-us/windows/iot-core/media/pinmappingsrpi/rp2_pinout.png)

In our case, we need the first four pins and we leave the SQW pin floating (unconnected). The sensor requires only 3V to run, but has regulators on board that can handle 5V. We must also use pull-up resistors on the SDA and SCL pins as it is good practice. The connection schematic is shown below:

![pcf8523_Layout](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Layouts/PCF8523_bb.png)

## Installing Necessary Packages
In order to use the TSL2591 sensor, we have to enable the I2C communication protocol. From the command line on the RPi:
1. Type ```$ raspi-config```
2. Choose ```Interfacing Options```
3. Navigate to ```P5 I2C```
4. When prompted, select ```<YES>```. 

Now that I2C has been configured, install the following python libraries:

### Circuit Python
General circuit-python library which will allow easy interfacing with Adafruti devices
```
$ pip3 install adafruit-circuitpython-lis3dh
```

### TSL2591
The library to read data from the sensor
```
$ pip3 install adafruit-circuitpython-pcf8523
```

## Testing the Sensor

Sample code can be found in the [Sample Code](Sample_Code/) directory. There is one file there: [Data Output Code](Sample_Code/pcf8523_dataoutput.py) - code that runs indefinitely and prints the current day and time.
