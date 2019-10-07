# Installation Instructions for the Sensirion SVM30 Multigas Sensor
This file contains instructions on how to connect and run the Sensirion SVM30 sensor for measuring total volatile organic compounds and temperature and relative humidity. For more information see the [datasheet](https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/Gas/Sensirion_Gas_Sensors_SVM30_Datasheet.pdf) on the sensor. 

## SVM30
![SVM30](https://cdn.sos.sk/productdata/59/fa/4fd31016/svm30-j.jpg)

## Connecting the SVM30
The SVM30 sensor does not come fully assembled, but with a four cable attachment, the sensor can be connected and tested to a breadboard. 

![SVM30_Pinout](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Images/svm30_pinout.png)

The RPi pinout is shown below for reference:

![RPI_Pinout](https://docs.microsoft.com/en-us/windows/iot-core/media/pinmappingsrpi/rp2_pinout.png)

In our case, we need the first four pins of the SCD30 and the last pin (SEL) connected to ground since we are using the I2C connection. The sensors require a minimum of 4.5V and the datasheet specifies that the SCL and SDA pins should be pulled to the ground. The schematic is shown below:

![SVM30_Layout](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Layouts/SVM30_bb.png)

## Installing Necessary Packages and Drivers
In order to use the SVM30 sensor, we have to get around some problems with the I2C communication protocol. First, make sure that I2C communication has been enabled by typing ```$ raspi-config```, choosing ```Interfacing Options```, navigate to ```P5 I2C```, and select ```<YES>```. 

Install the following python libraries:
```
$ sudo apt-get install python-crcmod
```
and to get around the complex I2C-commands, install:
```
$ sudo apt-get install pigpio python-pigpio
```

*Note: Do NOT install the python3 compatible versions of the above libraries. The code developed for using the SCD30 is not stable for python3*

## Two-in-One
The SVM30 sensor is unique compared to the other Sensirion sensors in that it is actually two sensors combined into one module:
1. [SGP30 Multigas Sensor](https://www.adafruit.com/product/3709)
2. [SHTC1 T/RH Sensor](https://www.sensirion.com/en/environmental-sensors/humidity-sensors/digital-humidity-sensor-for-consumer-electronics-and-iot/)

### SGP30 Multigas Sensor
Since this sensor was developed by Adafruit, there are libraries that make reading from this sensor trivial. For more information, see the documentation on the [SGP30 sensor](https://github.com/intelligent-environments-lab/bevobeacon2.0/blob/master/Setup/SGP30.md).

### SHTC1 T/RH Sensor
This sensor is not supported by Adafruit so libraries to connect this sensor have not been developed. Instead, processes similar to reading measurements from the [SCD30](https://github.com/intelligent-environments-lab/bevobeacon2.0/blob/master/Setup/Sensirion_SCD30.md) and [SPS30](https://github.com/intelligent-environments-lab/bevobeacon2.0/blob/master/Setup/Sensirion_SPS30.md) must be used. 

## Testing the Sensor

Sample code can be found in the [Sample Code](Sample_Code/SCD30/) directory. There is one file: [Data Logger Code](Sample_Code/scd30_datalogger.py) which runs indefinitely and writes the data to a csv file. **This code only works for the SGP30 sensor - the code to include T/RH has not been included.**
