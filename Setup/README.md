# BEVO Beacon IAQ Setup 

 The following sections detail how to setup the different components of the BEVO Beacon IAQ. Each section should be completed in the order written. 

## Raspberry Pi 3|B+
 This file outlines the basics of setting up a Raspberry Pi 3|B+ (RPi), outlining the necessary components/libraries needed, how to install the Raspbian Buster Lite Operating System (OS), and how to set up the OS properly. 

 ![RPi3](https://www.raspberrypi.org/app/uploads/2018/03/770A5842-1612x1080.jpg)

 ### Necessary Components
 The necessary components are as follows:
 - Rapsberry Pi 3|B+
 - Power supply (micro USB)
 - HDMI cable
 - microSD card
 - microSD card reader

 ### Installing Raspbian Buster Lite
 The OS can be found on Raspberry Pi's website [here](https://www.raspberrypi.org/downloads/raspbian/). There are multiple options, but Raspbian Buster Lite utilizes a no-nonsense, command line interface. 

 1. Download Raspbian Bust Lite from the Raspberry Pi website
   - Website link is in the description above
   - Download the latest zip file
 2. Flash the file onto the SD card
   - Etcher can flash the zip file onto the SD card
 3. Check if installation was successful 
   - Insert flashed SD card
   - Connect RPi to monitor via HDMI
   - Power up the RPi
   - Check to see if the RPi goes through the different power on protocols

 ### Connecting to WiFi
 The RPi 3|B+ has built-in WiFi capabilities meaning you can immediately connect your RPi to the internet. 

 1. From the command line on the RPi, navigate to the directory ```/etc/wpa_supplicant/``` and edit the *wpa_supplicant.conf* file.
 2. Add the following lines to set up a network, replacing the text in quotations with the name of your network and password:
 ```
 network={
   ssid="<NAME _OF_NETWORK>"
   psk="<PASSWORD_FOR_NETWORK>"
 }
 ```
 3. Perform a reboot with ```$ sudo shutdown -r now``` or ```$ sudo reboot```
 4. Check to see if the RPi connects to WiFi - there should be an IP address specified when rebooting

 ### Special Considerations for Connecting to utexas-iot WiFi
 If connecting to the utexas-iot network, additional steps are required before the first step in the previous section:

 1. From the command line on the RPi, type "ifconfig" and copy down the ethernet MAC address under "wlan0" 
 2. Navigate to UT's network [page](https://network.utexas.edu)
 3. Login with your UT EID and password
 4. Click "Register Wireless Device"
 5. Enter the MAC address you copied down earlier, give the device a name, and register
 6. A textbox will appear with the devices password. Now when you edit *wpa_supplicant.conf* in step 2 above, use "utexas-iot" as the ssid name and enter the password inside quotation marks with **no spaces** for the password. 

 ### Update RPi OS and Python
 Run the two lines below:
 ```
 $ sudo apt-get update
 $ sudo apt-get upgrade
 ```
 then install pip3 installer:
 ```
 $ sudo apt-get install python3-pip
 ```
 and upgrade setup tools:
 ```
 $ sudo pip3 install --upgrade setuptools
 ```

 ### Enable I2C and SPI
 Install supporting dependencies:
 ```
 $ sudo apt-get install -y python-smbus
 $ sudo apt-get install -y i2c-tools
 ```

 Both can be enabled via ```$ sudo raspi-config``` by selecting the appropriate communication from the interfaceing options. More detailed instructions (they are short) can be found at the following links:
 - [I2C](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c)
 - [SPI](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-spi)

### Cloning GitHub Repository
 Once connected to WiFi, using a GitHub repository makes updating and sharing files easy between two systems and others. The following steps will help to ensure that you can clone your GitHub repository to the RPi and start using git. 

 1. Check the Date
   - GitHub commands make queries that rely on the RPi having the correct time. 
   - Type ```$ date -R``` and make sure the time is correct. If the time is incorrect, type ```$ sudo apt-get install ntp```.
   This will allow the RPi to update the time. Be sure to do a ```$ sudo reboot``` after so the changes can take effect.
 2. Navigate to GitHub and copy down this repository's address.
 3. On the RPi install the git commands with ```$ sudo apt-get install git-core```
 4. Once installed, type ```$ git clone <GIT ADDRESS>``` to clone the repository on to the RPi.
 5. Move into the new directory and type ```$ git status``` to see if the clone worked correctly. 

 This repository holds all the necessary code needed to run the BEVO IAQ Sensor Platform. After setting up the Raspberry Pi, installing the necessary dependencies, and making all the hardware connections - the platform should be ready to go. 
 
### Installing Necessary Packages/Libraries
In addition to the packages specified above, the following set of packages have to be installed on to the RPi to use the current version of the code. 

#### Adafruit Sensors
To allow use of the adafruit sensors, one needs to run the following two commands:

**Light Sensor** ([TSL2591](https://www.adafruit.com/product/1980))
```
$ sudo pip3 install adafruit-circuitpython-tsl2591
```

**TVOC Sensor** ([SGP30](https://www.adafruit.com/product/3709))
```
$ sudo pip3 install adafruit-circuitpython-sgp30
```

#### Sensirion
To use the Sensirion sensors, one needs to install the following packages:

**Pi GPIO**
```
$ sudo apt-get install python-pigpio
```

**Checksum**
```
$ sudo apt-get install python-crcmod
```
 
## Sensor Hardware Connection
The next few sections outline how to connect the sensors to the RPi. 

### Prototyping
The schematic below shows one possible way to connect the sensors to the RPi via breadboard. From left to right in the schematic, the sensors represented are: SCD30, SVM30, SPS30, TSL2591, and RTC PCF8523. *Note: The sensors used in the schematic are NOT exact replicas.*

![bevo_iaq_bb](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Layouts/BEVO_IAQ_bb.png)

### Printed Circuit Board Development
A printed circuit board (PCB), shown below, was developed for this project. The PCB design does *not* allow for any direct connections to the board via headers except for the the RTC PCF8523 - the other sensors must be connected with wires.

![bevo_iaq_pcb](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Layouts/BEVO_IAQ_New_pcb.png)

The sensors in the schematic above, from top to bottom, are the SCD30, SVM30, SPS30, TSL2591, and PCF8523. The SVM30 and SPS30 are connected through the use of [5-pin female single connectors](https://images-na.ssl-images-amazon.com/images/I/41WAqkLeBJL._SL500_AC_SS350_.jpg) and [4-pin female single connectors](https://images-na.ssl-images-amazon.com/images/I/411g-Ag85ML._SL500_AC_SS350_.jpg), respectively. The remaining sensors can be connected to [male-to-female headers](http://img.dxcdn.com/productimages/sku_152192_2.jpg) soldered to the bottom of the board.

The PCB in the schematic shows the top view. The connections are routed on the bottom of the board and, from right to left, correspond to SCL, SDA, Vin, and Gnd. If there is a fifth connection, that connection is also ground i.e. SCL, SDA, Vin, Gnd, and Gnd. Two 4.7 k-Ohm resistors are connected at the top and second to bottom rows as pull-up resistors. 

## Code Development
(Under Construction)

