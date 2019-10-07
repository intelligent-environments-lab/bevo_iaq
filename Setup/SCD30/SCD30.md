# Installation Instructions for the Sensirion SCD30 Carbon Dioxide Air Quality Sensor
This file contains instructions on how to connect and run the Sensirion SCD30 sensor for measuring carbon monoxide. For more information see the [datasheet](https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/CO2/Sensirion_CO2_Sensors_SCD30_Datasheet.pdf) on the sensor. 

## SCD30
![SCD30](https://www.mouser.com/images/marketingid/2018/img/187534792_Sensirion_SCD30SensorModule.png)

## Connecting the SCD30
The SCD30 sensor does not come fully assembled, so the first task is soldering wires to create connections. The pinout is shown in the image below:

![SCD30_Pinout](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Images/scd30_pinout.png)

The acronyms correspond to:
1. **VDD**: Voltage supply
2. **GND**: Ground connection
3. **TX/SCL**: Modbus: Transmission line (Push/Pull with 3V level) I2C: Serial clock (internal 45kΩ pull-up resistor, pulled to 3V)
4. **RX/SDA**: Modbus: Receive line (Input must not exceed 5.5V) I2C: Serial data (internal 45kΩ pull-up resistor, pulled to 3V)
5. **RDY**: Data ready pin - high when data is ready for read-out
6. **PWM**: Pulse-Width Modulation output of CO$_2$ concentration measurement
7. **SEL**: Interface select pin. Pull to VDD (do not exceed 4V, use voltage divider in case your VDD is >4V) for selecting Modbus, leave floating or connect to GND for selecting I2C.

The RPi pinout is shown below for reference:

![RPI_Pinout](https://docs.microsoft.com/en-us/windows/iot-core/media/pinmappingsrpi/rp2_pinout.png)

In our case, we need the first four pins of the SCD30 and the last pin (SEL) connected to ground since we are using the I2C connection. The sensors require 3V or less so we must use pull-up resistors on the SDA and SCL pins. The schematic is shown below:

![SCD30_Layout](https://github.com/intelligent-environments-lab/bevo_iaq/blob/master/Setup/Images/scd30_pinout.png/SCD30_bb.png)

## Installing Necessary Packages and Drivers
In order to use the SCD30 sensor, we have to get around some problems with the I2C communication protocol. First, make sure that I2C communication has been enabled by typing ```$ raspi-config```, choosing ```Interfacing Options```, navigate to ```P5 I2C```, and select ```<YES>```. 

Install the following python libraries:
```
$ sudo apt-get install python-crcmod
```
and to get around the complex I2C-commands, install:
```
$ sudo apt-get install pigpio python-pigpio
```

*Note: Do NOT install the python3 compatible versions of the above libraries. The code developed for using the SCD30 is not stable for python3*

### I2C Clock Stretching
The default on the RPi is too low and we need Clock Stretching up to 150ms. To set it, download the three files from this [GitHub directory](https://github.com/raspihats/raspihats/tree/master/clk_stretch).

Now compile the following two drivers:
```
gcc -o i2c1_set_clkt_tout i2c1_set_clkt_tout.c
gcc -o i2c1_get_clkt_tout i2c1_get_clkt_tout.c
```

Execute (?) the following execute (add to /etc/rc.local to run on every boot):
```
./i2c1_set_clkt_tout 20000 # for 200ms
```

*Note: The above execute command is a mystery to me. Not quite sure what it does especially since an error was thrown, but the sample code is still able to run*

## Testing the Sensor

Sample code can be found in the [sample code](Sample_Code/) directory. There is one file there: [Data Logger Code](Sample_Code/scd30_datalogger.py). This code runs indefinitely and writes the data to a csv file. 

