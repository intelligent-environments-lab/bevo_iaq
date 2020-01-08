# Installation Instructions and Documentation for the Sensirion SPS30 Pariculate Matter Sensor
This file contains instructions on how to connect and run the Sensirion SPS30 sensor for measuring particulate matter. For more information see the [datasheet](https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/Particulate_Matter/Sensirion_PM_Sensors_SPS30_Datasheet.pdf) on the sensor. 

## SPS30
![SPS30](https://www.mouser.be/images/marketingid/2018/img/106742304.png)

## Hardware Connection for the SPS30
The SPS30 requires a connection for the 5 pins on the sensor. The pinout for the SPS30 is shown below:

![SPS30_Pinout](Images/sps30_pinout.png)

The acronyms are described in the image above. This document and setup is for I2C communication which means when connecting the SPS30 to RPi, the SEL pin (pin 4) should be connected to GND. We will also be using the SDA/SCL pins on the RPi to set up the connection. The RPi pinout is shown below for reference:

![RPI_Pinout](https://docs.microsoft.com/en-us/windows/iot-core/media/pinmappingsrpi/rp2_pinout.png)

In our case, we need all five pins of the SPS30 with the fourth pin (SEL) connected to ground. The sensors require around 5V and we must use pull-up resistors on the SDA and SCL pins. The connection schematic is shown below:

![SPS30_Layout](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Layouts/SPS30_bb.png)

## Installing Necessary Packages and Drivers
In order to use the SPS30 sensor, we have to get around some problems with the I2C communication protocol. First, make sure that I2C communication has been enabled on the RPi. From the command line on the RPi:
1. Type ```$ raspi-config```
2. Choose ```Interfacing Options```
3. Navigate to ```P5 I2C```
4. When prompted, select ```<YES>```. 

Now that I2C has been configured, install the following python libraries:

### Checksum
For easy [checksum calculations](https://www.lifewire.com/what-does-checksum-mean-2625825), the following library will be installed to help:
```
$ sudo apt-get install python-crcmod
```

### Pigpiod
To get around the complex I2C-commands, install:
```
$ sudo apt-get install pigpio python-pigpio
```

*Note: Do NOT install the python3 compatible versions of the above libraries. The code developed for using the SPS30 is not stable for python3 and currently under construction*

## Testing the Sensor

Sample code can be found in the [Sample Code](Sample_Code/SPS30/) directory. There are two files there:
1. [Sample Code](Sample_Code/SPS30/sps30_sample.py) - code that measures one value upon running
2. [Data Logging Code](Sample_Code/SPS30/sps30_datalogger.py) - code that runs indefinitely and logs data in a csv file

The overview of the I2C commands is below and also included in the [datasheet](https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/Particulate_Matter/Sensirion_PM_Sensors_SPS30_Datasheet.pdf):

![SPS30_Commands](Images/sps30_i2c_commands.png)

### Code Breakdown
The following sections look at important aspects of the two files above to help shed light on how to communicate with the sensor. 

#### Important Definitions
The code incorporates some important variable definitions that deserve a more elaborate explanation

##### PI-GPIO
The [PI-GPIO library](http://abyz.me.uk/rpi/pigpio/) is a library for the RPi which allows control of the General Purpose Input Outputs (GPIO) pins. 
```python
PIGPIO_HOST = '127.0.0.1' # local host
pi = pigpio.pi(PIGPIO_HOST)
```

##### Connecting the Device
With RPi GPIOs defined with the pigpio library, we can create a connection to the device if we know the I2C bus and slave(s). 
```python
I2C_SLAVE = 0x69 # Given in datasheet for SPS30
I2C_BUS = 1
h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
```

##### Creating the Checksum Function
The following code allows for easier checksum calculations but is currently a MyStErY:
```python
f_crc8 = crcmod.mkCrcFun(0x131, 0xFF, False, 0x00)
```

#### I2C Write
The following is the *i2cWrite()* function
```python
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
```

This function helps to simplify writing commands to the RPi via *i2c_write_device()*. The input is an array of bytes that are written to the sensor via the connection `h`. Different commands can be found in the table above for the SPS30. The data has to be given in chunks (see other functions below). 

#### Reading Bytes from the Sensor
This function is the one that actually gathers data from the sensor. The data are returned as a string of bytes that should be the length specified by the `n` input. 
```python
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
    exit(1)

  if count == n:
    return data
  else:
    eprint("error: read bytes didnt return " + str(n) + "B")
    return False
```
    
The device reads in the data and if the number of bytes read from the sensor (`count`) matches that specified in the input, then the data are returned. 

#### Reading from the Command Address
The *readFromAddr()* function is similar to [*i2cWrite()*](#i2c-write), but reads the number of bytes using the command specified from the `LowB` and `HighB` inputs.
```python
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
```

#### Start Measurement
The following is the *startMeasurement()* function
```python
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
```

This function is the first that emplots the *i2cWrite()* function. The commands for starting the measurement (0x0010), reading values (0x0300), and performing a checksum on the measurement reading are given placed in array as input to the *i2cWrite()* function. The important item to note here is that the command has to be broken into two parts i.e. 0x0010 = [0x00,0x10]. This notation will be true for any of the commands written to the sensor. 

### Supplementary Functions
These functions, while still integral to the operation of the [sample code](#testing-the-sensor), are more self-explanatory then the ones mentioned above.

#### Print Human
The *printHuman()* function prints an output of the data to the terminal screen. While this might not be the most exciting function, it exhibits some important aspects of the sensor i.e. the portions of the string of numbers in the data that correspond to the different PM counts and concentrations.
```python
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
```

The following figure is taken from the datasheet that corroborates the byte numbers above with the data string:

![SPS30_MISO1](Images/sps30_miso1.png)
![SPS30_MISO2](Images/sps30_miso2.png)

#### Reset
The *reset()* function is shown below
```python
def reset():
  for i in range(5):
    # RESET: 0xD304
    ret = i2cWrite([0xd3, 0x04])
    if ret == True:
      return True
    eprint('reset unsuccessful, next try in', str(0.2 * i) + 's')
    time.sleep(0.2 * i)
  eprint('reset unsuccessful')
  return False
```

The *reset()* function shutdowns the device and restarts the software which is useful if power on is not successful.

### Big Rest
The *bigReset()* function is given below:
```python
def bigReset():
  global h
  eprint('resetting...',end='')
  pi.i2c_close(h)
  time.sleep(0.5)
  h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
  time.sleep(0.5)
  reset()
  time.sleep(0.1) # note: needed after reset
```

The difference between the [*reset()*](#reset) function and the *bigReset()* is that the communication between the RPi and the device is closed and reopened. This function is useful to call if communication is not succuessful on power on. 

## Resources
A large majority of the code was pulled from the repository [here](https://github.com/UnravelTEC/Raspi-Driver-SCD30)
