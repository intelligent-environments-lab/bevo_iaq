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
 
### Attaching to Virtual Private Network (VPN)

#### Logmein Hamachi
The older generations of the BEVO Beacons were connected to users through the Logmein Hamachi VPN. 

##### Resources
1. [General Process](https://medium.com/@KyleARector/logmein-hamachi-on-raspberry-pi-ad2ba3619f3a)
2. [Exception when using RPi Zero](https://community.logmein.com/t5/LogMeIn-Hamachi-Discussions/Raspberry-Pi-quot-illegal-instruction-quot/td-p/201479)

#### Tailscale
Tailscale is a similar version to Logmein Hamachi, but a free, more simplified version. 

##### Resources
1. [Installing](https://tailscale.com/kb/Install)
1. [Installing on RPi](https://tailscale.com/kb/1043/install-raspbian-buster)
2. [Using Auth Keys](https://tailscale.com/kb/1085/auth-keys)

 ### Update RPi OS and Python
 Run the two lines below:
 ```
 $ sudo apt-get update
 $ sudo apt-get upgrade
 ```
 then install pip and pip3 installer:
 ```
 $ sudo python get-pip.py
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
 
### Installing Necessary Sensor Packages/Libraries
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

**OLED Screen** ([SSD1306](https://learn.adafruit.com/micropython-hardware-ssd1306-oled-display/circuitpython))
```
# sudo pip3 install adafruit-circuitpython-ssd1306
```

#### Sensirion
To use the Sensirion sensors, one needs to install the following packages:

**Pi GPIO** ([Documentation](http://abyz.me.uk/rpi/pigpio/python.html))
```
$ sudo apt-get install python-pigpio
```
The Pi GPIO needs to be activiated on every boot of the RPi, so to ensure that this happens each time you can edit the bash file. From anywhere, type:
```
$ sudo nano ~/.bashrc
```
At the bottom of the file, add the two lines of code:
```python
# To activate Pi GPIO
sudo pigpiod
```

**Checksum** ([Documentation](http://crcmod.sourceforge.net/crcmod.html#module-crcmod))
```
$ sudo apt-get install python-crcmod
```

### Using Amazon Web Services
First to use Amazon Web Services (AWS), we need to install a few packages. For AWS to work with both sensor brands, we need use both versions of pip to get it to work for Python 2 and 3. 
```
$ sudo pip install boto3
$ sudo pip3 install boto3
```

The code supports the use of RPi profiles which means one must edit the ```/etc/profile``` of the RPi. The following lines should be added to the bottom of the file, with your appropriate string value within the angled brackets:
```C
export AWS_ACCESS_KEY_ID='<AWS_ACCES_KEY_ID>'
export AWS_SECRET_ACCESS_KEY='<AWS_SECRET_ACCESS_KEY>'
export BUCKET_NAME='<BUCKET_NAME>'
```

**NOTE**: You must type the above lines EXACTLY as you see them. Any extra spaces added will make the exports unusable. 
 
## Sensor Hardware Connection
The next few sections outline how to connect the sensors to the RPi. 

### Prototyping
The schematic below shows one possible way to connect the sensors to the RPi via breadboard. From left to right in the schematic, the sensors represented are: SCD30, SVM30, SPS30, TSL2591, and RTC PCF8523. *Note: The sensors used in the schematic are NOT exact replicas.*

![bevo_iaq_bb](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Layouts/BEVO_IAQ_bb.png)

### Printed Circuit Board
A printed circuit board (PCB), shown below, was developed for this project. The PCB design does *not* allow for any direct connections to the board via headers except for the the RTC PCF8523 - the other sensors must be connected with wires.

![bevo_iaq_pcb](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Layouts/BEVO_IAQ_New_pcb.png)

The sensors in the schematic above are labeled, and from top to bottom are:
1. SCD30 - Carbon Dioxide, Temperature, and Relative Humidity
2. SVM30 - Total Volatile Organic Compounds
3. SPS30 - Particulate Matter
4. TSL2591 - Light
5. PCF8523/DS1307 - Real-Time Clock
6. SSD1306 - OLED Screen

The remaining sensors are be connected with female-to-female wires after soldering male-to-male header pins to both the PCB and each individual sensor. The PCB in the schematic shows the top view where the connections are routed on the bottom of the board. There are five columns of connections on the PCB. From left to right, these columns represent specific pin connections:
1. Extra GND connection - needed for SCD30 and SPS30 SEL pins
2. GND connection
3. Vin connection
4. Serial Data (SDA) connection
5. Serial Clock (SCL) connection

Two 4.7 k-Ohm resistors are connected at the top and bottom as pull-up resistors. 

The SVM30 and SPS30 are connected through the use of [5-pin female single connectors](https://images-na.ssl-images-amazon.com/images/I/41WAqkLeBJL._SL500_AC_SS350_.jpg) and [4-pin female single connectors](https://images-na.ssl-images-amazon.com/images/I/411g-Ag85ML._SL500_AC_SS350_.jpg), respectively.

For the remaining sensors, wires are cut, crimped, and plugged in with the following specifications:
1. **SCD30**
 - Wires: blue, black, red, yellow, and green wires each cut to a length of 3 inches
 - Female to Female connections:
  - PCB Connection: 5x1 blue, black, red, yellow, green
  - Sensor Connection: 4x1 red, black, green, yellow; 1x1 blue
 - i2c Address: 61
 - Layout:
 
 ![pcb-scd30](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Images/PCB%20-%20SCD30.png)
 
 2. **SVM30**
 *Note: Connectors are provided - wires do not need to be crimped*
 - Wires: red, white, yellow, black
 - Wire to connector
 - i2c Address(es): 58 and 70
 - Layout: 
 
 ![pcb-svm30](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Images/PCB%20-%20SVM30.png)
 
 3. **SPS30**
 *Note: Connectors are provided - wires do not need to be crimped*
 - Wires: red, black, navy, green, yellow
 - Wire to connector
 - i2c Address(es): 69
 - Layout: 
 
 ![pcb-sps30](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Images/PCB%20-%20SPS30.png)
 
 4. **TSL**
 - Wires: black, red, yellow, green
 - Female to Female connections
  - PCB Connection: 4x1 black, red, yellow, green
  - Sensor Connection: 2x1 red, black; 2x1 yellow, green 
 - i2c Address: 29
 - Layout: 
 
 ![pcb-tsl](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Images/PCB%20-%20TSL.png)
 
 5. **RTC**
 - Wires: black, red, yellow, green
 - Female to Female connections
  - PCB Connection: 4x1 black, red, yellow, green
  - Sensor Connection: 4x1 red, black, yellow, green
 - i2c Address: 68 (changes to UU once connected)
 - Layout:
 
 
 
 6. **OLED**
 - Wired: black, red, yellow, green
 - Female to Female connections
  - PCB Connection: 4x1 black, red, yellow, green
  - Sensor Connection: 4x1 red, black, yellow, green
 - i2c Address: 3c
 - Layout:
 
 
 
 6. **RPi**
 - Wires: black, red, yellow, green
 - Female to Female connections
  - PCB Connection: 4x1 red, black, yellow, green
  - RPi Connection: 5x2 (top row) red, red (fan), black, space, space (bottom row) space, yellow, green, space, black
 - Layout:
 
 ![rpi-pcb](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Images/RPi%20-%20PCB%20and%20Fan.png)

### Real-Time Clock Setup
The link to setup three different real-time clocks is found [here](https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/set-rtc-time). 

## Code Development
(Under Construction)

### Running Code on Startup
With the code ready to run, we can enable it to run on boot of the RPi. To do so we can create service files that are run during the normal power-on process. 
1. Create the .service files (there are three such files in located [here](https://github.com/intelligent-environments-lab/bevo_iaq/tree/master/Setup/Code)
2. Place the .service files in the ```/etc/systemd/system/``` directory
3. You can test your service files before enabling them by typing ```$ sudo systemctl start your_service.service``` and then you can stop the test by typing ```$ sudo systemctl stop your_service.service```
4. Once you are ready, enable the service by typing ```$ sudo systemctl enable your_service.service```
5. Reboot your RPi and the service should run on boot in the background. 

See [here](https://www.raspberrypi.org/documentation/linux/usage/systemd.md) for ruther reading.

## Calibration
(Under Construction)
Due to the nature of low-cost sensors, calibration needs to occur in order to improve their accuracy. 

### SPEC Sensor Initial Calibration
The SPEC sensors need an initial calibration to identify the sensitivity factor. Since the SPEC sensors are the only sensors using serial communication, we have to use a program like [picocom](https://linux.die.net/man/8/picocom) to communicate with them. The following steps allow you to view the output of the SPEC sensors:
1. The SPEC sensors are connected via USB so check to see if they are any USB devices by typing either ```$ lsusb``` or changing into the ```/dev/``` directory and listing all directories/files. In the first case, you should see two devices that start with the name "Cyngal Integrated Products". In the latter, look for "ttyUSB0" and "ttyUSB1" in the ```/dev/``` directory.
2. Use picocom to connect to one of the USB devices (0 or 1) with:
```$ sudo picocom /dev/ttyUSB0```
3. You can check which sensor you are communicating with by typing "e"
4. These sensors need a continuous source of power to function most effectively. When you initially connect them, you should let them run for at least an hour or until the concentration has settled out. To see the measurement values, you have two options:
 1. Pressing enter will return one measurement
 2. Typing "c" will start the continuous measurement, and values will be reported every second.
5. The output is the following: serial number, concentration (ppb), temperature (C), relative humidity, raw value 1, raw value 2, raw value 3, number of days, then hours, then minutes, then seconds that the sensor has been on. 
6. Type "c" and check to see that the concentrations are in relative agreement. If this is the case, you can type "r" to get out of continuous measurement. 
7. If the concentration is stable, you have two options: zero the sensor or specify the concentration in the room:
 1. If the concentration of the pollutant is zero, type "Z" to zero the sensor.
 2. if the concentration of hte pollutant is known, type "S XXX" with the known concentration in ppm.
