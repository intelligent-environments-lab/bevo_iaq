"""Display Script

This script coordinates the measurements displayed on the OLED screen of the Beacon.

Intelligent Environments Lab (IEL), The University of Texas at Austin
Author: Hagen Fritz
Project: BEVO Beacon IAQ
    - Contact: Hagen Fritz (hagenfritz@utexas.edu)
"""

import os
import glob
import logging
import pathlib
import argparse

import board
import busio as io

import pandas as pd
import numpy as np
import time

from oled_text import OledText, BigLine, SmallLine

def get_measurements(variables,path_to_data="/home/pi/DATA"):
    """
    Gets the latest measurements from the data file

    Parameters
    ----------
    variables : list of str
         raw variable name(s) in the dataframe columns
    units : list of str
        units for variable(s)
    names : list of str
        display name(s) for the variables
    path_to_data : str 
        path to the raw data

    Returns
    -------
    measurements : list of lists 
        inner list corresponds to the variable, unit, and display name
    """
    # logging instance
    logger = setup_logging("get_measurements")
    # getting newest file
    file_list = glob.glob(f"{path_to_data}/*.csv")
    newest_file = max(file_list, key=os.path.getctime)
    logger.info(f"Reading from {newest_file}")
    beacon = int(newest_file.split("/")[-1][1:3])
    # reading in file
    df = pd.read_csv(f"{newest_file}",index_col=0)
    # getting important var measurements
    measurements = []
    for v in variables:
        try:
            value = df.loc[:,v].values[-1]
            # correcting the value 
            corrected = False
            path_to_correction = "/home/pi/bevo_iaq/bevobeacon-iaq/correction/"
            if os.path.exists(path_to_correction):
                for file in os.listdir(path_to_correction):
                    file_info = file.split("-")
                    short_name = get_short_name(v.split('-')[0])
                    if file_info[0] == short_name:
                        logger.warning(f"Found correction file for {short_name}")
                        correction = pd.read_csv(f"{path_to_correction}{file}",index_col=0)
                        corrected = True
                        break

            if corrected is False:
                logger.warning(f"No correction file for {v} (looked for {short_name})")
                correction = pd.DataFrame(data={"beacon":np.arange(0,51),"constant":np.zeros(51),"coefficient":np.ones(51)}).set_index("beacon")
                
            value = value * correction.loc[beacon,"coefficient"] + correction.loc[beacon,"constant"]
        except KeyError:
            logger.exception(f"Check parameter name: {v}")
            value = np.nan
            
        measurements.append(round(value,1))

    return measurements

def get_short_name(param):
    """
    Gets the short name for a given parameter

    Parameters
    ----------
    param : str
        name of the parameter to look up

    Returns
    -------
    <short_name> : str
        shortened name
    """
    if param in ["carbon_dioxide","co2"]:
        return "co2"
    elif param in ["carbon_monoxide","co"]:
        return "co"
    elif param in ["t_from_no2","t_from_co2","t_from_co"]:
        return "temperature_c"
    else: # no change needed
        return param

def get_display_name(param):
    """
    Gets the display name for a given parameter
    
    Parameters
    ----------
    param : str
        name of the parameter to look up

    Returns
    -------
    <display_name> : str
        name to display for parameter
    
    """
    if param in ["carbon_dioxide","co2"]:
        return "Carbon Dioxide"
    elif param in ["carbon_monoxide","co"]:
        return "Carbon Monoxide"
    elif param in ["pm1_mass","pm2p5_mass","pm10_mass"]:
        return "Particulate Matter"
    elif param in ["t_from_no2","t_from_co2","t_from_co"]:
        return "Temperature"
    else: # no change needed
        return param

def get_display_unit(param):
    """
    Gets the display name for a given parameter
    
    Parameters
    ----------
    param : str
        name of the parameter to look up

    Returns
    -------
    <display_name> : str
        name to display for parameter
    
    """
    if param in ["c","f"]:
        return param.upper()
    elif param == "microgram_per_m3":
        return "ug/m" #exponent needs to be taken care of separately
    else: # no change needed
        return param

def setup_logging(log_file_name):
    """
    Creates a logging object

    Parameters
    ----------
    log_file_name : str
        how to name the log file

    Returns
    -------
    logger : logging object
        a logger to debug
    """
    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Create handlers
    c_handler = logging.StreamHandler()
    dir_path = pathlib.Path(__file__).resolve().parent
    f_handler = logging.FileHandler(f'{dir_path}/{log_file_name}.log',mode='w')
    c_handler.setLevel(logging.WARNING)
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s: %(name)s (%(lineno)d) - %(levelname)s - %(message)s',datefmt='%m/%d/%y %H:%M:%S')
    f_format = logging.Formatter('%(asctime)s: %(name)s (%(lineno)d) - %(levelname)s - %(message)s',datefmt='%m/%d/%y %H:%M:%S')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

def main(sleep_time=3):
    logger = setup_logging("display")
    # creating i2c instance
    i2c = io.I2C(board.SCL, board.SDA)

    # creating sensor object (i2c object, height, width)
    oled = OledText(i2c, 128, 64)
    # layout 
    oled.layout = {
        1: SmallLine(2, 4, font="FreeSans.ttf", size=12), # title
        2: BigLine(5, 20, font="FreeSans.ttf", size=24), # value
        3: BigLine(80, 24, font="FreeSans.ttf", size=18), # unit
        4: BigLine(74, 20, font="FontAwesomeSolid.ttf",size=10), # degree
        5: SmallLine(120, 20, font="FreeSans.ttf", size=8), # exponent
        6: SmallLine(2, 50, font="FreeSans.ttf", size=12), # name
    }
    oled.text("WCWH BEVO Beacon",1)

    while True:
        # Getting Newest Measurements
        # ---------------------------
        # standard 
        variables=["carbon_dioxide-ppm","pm2p5_mass-microgram_per_m3","carbon_monoxide-ppb","t_from_no2-c"]
        m = get_measurements(variables=variables) 
        # Displaying Measurements
        # -----------------------
        try:
            for variable, value in zip(variables,m):
                name = variable.split("-")[0]
                unit = variable.split("-")[-1]
                logger.info(f"Displaying {name}: {value} {unit}")
                if name in ["carbon_monoxide","co","Carbon Monoxide"]:
                    logger.info("Converting raw CO measurements to ppm")
                    value /= 1000
                    value = round(value,1)
                    
                if unit == "F":
                    logger.info("Converting to F")
                    value = round(1.8*value+32,2)

                oled.text(f"{value}",2) # output of measured value
                oled.text(f"{get_display_unit(unit)}",3) # output of the variable
                if unit in ["c","C","F","f"]: # adding degree symbol for temperature
                    oled.text(f"\uf22d",4)
                    oled.text(f"",5)
                elif unit in ["ug/m","microgram_per_m3"]: # adding exponent for pm
                    oled.text(f"",4)
                    oled.text(f"3",5)
                else: # no output on these "lines"
                    oled.text(f"",4)
                    oled.text(f"",5)

                oled.text(f"{get_display_name(name)}",6) # output of the display name

                oled.show()
                time.sleep(sleep_time) # holding display
        except OSError:
            logger.exception("Error:")
            oled.clear()
            oled.text(f"ERROR",3)
            time.sleep(sleep_time)

# Execution Start
# ------------------------------------------------------------------------- #
if __name__ == '__main__':
    """ 
    Generates the figures used in the dashboard
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help="number of seconds to display a measurement", default=3, type=int)
    args = parser.parse_args()
 
    main(sleep_time=args.t)
# ------------------------------------------------------------------------- #
