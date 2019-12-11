# Bevo Beacon IAQ
This document details the basics of the Building EnVironment and Occupancy (BEVO) Beacon with enhanced Indoor Air Quality (IAQ) monitoring. 

## Variables Measured

The BEVO IAQ, in its second iteration, will be able to monitor:
-	**Temperature/Relative Humidity**: influences thermal comfort 
-	**Carbon Dioxide**: Associated with ventilation rates and high concentrations have been shown to impair cognitive function
-	**Total Volatile Organic Compounds**: Any airborne organic compound commonly associated with cleaning products that may cause upper respiratory irritation 
-	**Particulate Matter**: Any airborne solid/liquid particles such as dust, pollen, or particles in smoke that are associated with inflammation/irritation of upper respiratory system
- **Nitrogen Dioxide**: Similar to sulfur dioxide
- **Carbon Monoxide**: Indoor air pollutant associated with incomplete combustion processes
-	**Light Level**: To help determine when lights are on or off

## Sensors
The following subsections outline the various sensors that will be incorporated into the first BEVO IAQ model.

### Sensirion SCD30

![SCD30](https://www.mouser.com/images/marketingid/2018/img/187534792_Sensirion_SCD30SensorModule.png)

The SCD30 sensor is capable of measuring the following:
- Temperature
- Relative Humidity
- Carbon Dioxide Concentrations (in parts-per-million)

More on how to connect the sensor can be found in the [setup](Setup/SCD30) directory of this repository. Sample code is also provided in the same directory.

### Sensirion SVM30

![SVM30](https://www.mouser.in/images/marketingid/2019/img/183817211.png)

The SVM30 sensor is actually a combination of two sensors: the SHT1C Temperature/Relative Humidity Sensor and the SGP30 Total Volatile Organic Compounds (TVOCs) sensor. The SVM30 is capable of measuring the following:
- Temperature
- Relative Humidity
- TVOCs in parts-per-billion
- TVOCs in equivalent Carbon Dioxide concentrations

Since the SCD30 already measures temperature and relative humidity, we do not need to use the SHT1C sensor included on the SVM30 especially since interfacing with this sensor is complicated. We only need to interact with the SGP30 sensor that is built into the SVM30. The SGP30 is an Adafruit sensor and has good documentation/well-developed libraries online that we can take advantage of. More on how to connect to and read from the sensor can be found [here](Setup/SVM30).

### Sensirion SPS30

![SPS30](https://www.mouser.be/images/marketingid/2018/img/106742304.png)

The SPS30 sensor is capable of measuring the following:
- Particulate Matter (PM) Counts for particles  of 0.5, 1, 2.5, 4, and 10 micrometers in diameter in #/dL
- PM Concentrations for particles of 1, 2.5, 4, and 10 micrometers in diameter in $\mu$g/m$^3$

More on how to connect to and collect readings from the sensor can be found [here](Setup/SPS30).

### Adafruit TSL2591

![TSL](https://asset.conrad.com/media10/isa/160267/c1/-/de/1516629_BB_00_FB/erweiterungsboard-tsl2591-high-dynamic-range-digital-light-sensor-adafruit-1980-1516629.jpg)

The TSL sensor is capable of measuring the following:
- Infrared level
- Full-spectrum
- Human-visible light (in lux)

More on how to connect to and collect readings from the sensor can be found online [here]() or through the [setup](Setup/TSL) directory in this repository. 

### SPEC 

