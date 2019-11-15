/*
  DSDK_RUN2 - Example use of library for reading KWJ Engineering with SPEC Sensors on Digital SDK.
  Created by David E. Peaslee, March 29, 2018.
  Created for SPEC/KWJ Digital Gas Sensor (DGS, or also known as DULPSM)
  Not yet released into the public domain.


  !!! RX, TX Must be on 3.3 volt communication, or using level shifters to get to 3.3V UART!!!

  Wiring:
  Connect the TX of Digital Sensor to the RX of 3.3 V Arduino
  Connect the RX of Digital Sensor to the TX of 3.3 V Arduino
  Connect the power of Digital Sensor to the 3.3V power of the Arduino
  Connect the ground of Digital Sensor to the ground of the Arduino

  This code is optimized for the Arduino Due, but can be modified to work with any other Arduino.
  The DGS is a 3.3V device, which means you must use level shifters if using with a 5V Arduino.

  DGS runs at 9600 baud rate.
*/

/*This example requires the DGS libraries, if it does not compile look to the library.properties file and add your board to the architectures.
   The purpose of this example is to help you set up the DGS. After the first setup, loading the barcode into the DGS, you do not need to
   repeat the setup portion of the DGS commands. You only need to initialize the serial ports in Setup.

   !You need to set up sensors using the DSDK_SETUP sketch!

   You can re-zero at anytime by sending Z through the serial terminal, once the continuous output starts. If you require technical assistance, please grab a
   screen shot of the BarCode text, as well as the output of the EEPROM, and the Firmware Date. To turn off verbose setup, change DEBUG to false.

*/
#include "DGS.h"

DGS mySensor(&Serial);

void setup() //Setup intended for first time setup of SDK. Must initialize both serial ports:
{
  Serial.begin(9600);
  Serial.flush();
  Serial.println("Begin Setup");

  mySensor.DEBUG = false;

  //Remainder of setup() code is only necessary for initial setup of DULP
  Serial.println();
  Serial.println(mySensor.getFW());  // Retruns FW date
  Serial.println();

  mySensor.getEEPROM();  //Read eeprom into array and/or list view if DEBUG is TRUE. See end of sketch for outline of values.
  Serial.println();

  Serial.println("Enter 'Z' When Sensor is Stabilized");
  while (Serial.read() != 'Z') {}
  if (mySensor.zero()) Serial.println("Finished Setting Sensor1 Zero"); //zeros returns 1/0
  Serial.println();

  Serial.println("Finished Setup");
}

void loop()
{
  mySensor1.getData('\r');

  Serial.print("Concentration = ");
  Serial.print(mySensor.getConc());     //default is 'p' for temperature compensated ppb, any other cahracter for raw counts

  Serial.print(", Average Temperature = ");

  Serial.print(mySensor.getTemp('F')); //'F' or 'C' for units of temperature, default is 'C', any other cahracter for raw counts

  Serial.print(", Average Humidity = ");

  Serial.println((mySensor.getRh());   //default is 'r' for %Rh, any other character for raw counts

  while (Serial.available()) // read from Serial port, send to port SDK port
  {
    char U = Serial.read();
    if (U == 'Z') {
      if (mySensor.zero()) Serial.println("Finished Setting Sensor 1 Zero"); //zeros returns 1/0
    }
    if (U == 'f') {
      Serial.println(mySensor.getFW());
    }
    if (U == 'e') {
      mySensor.DEBUG = true;
      mySensor.getEEPROM();
    }
  }
}

/*
    EEPROM Values can be called using the following addresses (Ex. mySensor.e[1] is int and mySensor.E[1] is String)

    nA_per_PPM_x100 = eepromInt[1]
    ADC_OC = eepromInt[2]
    ADC_Zero = eepromInt[3]
    ADC_Span = eepromInt[4]
    Temperature_Offset_x1000 = eepromInt[5]
    T_Zero = eepromInt[6]
    RH_Zero = eepromInt[7]
    T_Span = eepromInt[8]
    RH_Span = eepromInt[9]
    LMP91000 Register 0x10 = eepromInt[10]
    LMP91000 Register 0x11 = eepromInt[11]
    LMP91000 Register 0x12 = eepromInt[12]
    Average_Total = eepromInt[13]
    Barcode = eepromStr[0]
    Serial_Number_ = eepromStr[1]
    Part_Number = eepromStr[2]
    Gas = eepromStr[3]
    Date_Code = eepromStr[4]
    Sensitivity_Code = Sensitivity_Code
*/
