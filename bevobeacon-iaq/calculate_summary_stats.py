"""BEVO Beacon - Calculate Summary Stats

This script takes data from the raw csv files stored on the device and creates
a new file holding summary statistics.

Intelligent Environments Laboratory (IEL), The University of Texas at Austin
Author: Hagen Fritz
Project: BEVO Beacon
    - Contact: Hagen Fritz (hagenfritz@utexas.edu)
"""
import sys
import json

import pandas as pd
import numpy as np

from datetime import datetime

class Calculate:

    def __init__(self,beacon,data_dir="~/DATA/",save_dir="~/summary_data/") -> None:
        """
        Initializing Function

        Parameters
        ----------
        beacon : str
            number assigned to the beacon
        data_dir : str, default "~/DATA/"
            path to raw data
        save_dir : str, "~/summary_data/"
            path to save location

        Creates
        -------
        data_dir : str
            location of the raw data
        save_dir : str
            location to save data
        date : datetime.date
            file/calculation date
        data : DataFrame
            raw data
        """
        # read/save locations
        self.data_dir = data_dir
        self.save_dir = save_dir

        self.date = datetime.now().date()
        date_str = datetime.strftime(self.date,"%Y-%m-%d")
        self.data = pd.read_csv(f"{self.data_dir}/b{beacon}_{date_str}.csv")

    def get_statistics(self,iaq_params={"CO2":1100,"PM_C_2p5":12,"CO":4,"T_NO2":27,"RH_NO2":60}):
        """
        Calculates summary statistics

        Parameters
        ----------
        iaq_params : dict, default {"CO2":1100,"PM_C_2p5":12,"CO":4,"T_NO2":27,"RH_NO2":60}
            pollutants to consider with thresholds- strings much match the columns from the RAW data

        Returns
        -------
        res : dict of dict
            dictionary indexed by pollutant containing dictionaries with summar statistics
        """
        res = {} # overall results
        for iaq_param in iaq_params.keys():
            iaq_res = {} # specific parameter results
            for stat_str, fxn in zip(["min","mean","median","max"],[np.nanmin,np.nanmean,np.nanmedian,np.nanmax]):
                iaq_res[stat_str] = fxn(self.data[iaq_param])
            data_above_threshold = self.data[self.data[iaq_param] > iaq_params[iaq_param]]
            iaq_res["time_above_threshold"] = len(data_above_threshold) # this assumes a 1-minute resolution on the data
            res[iaq_param] = iaq_res

        return res

    def save(self,d,save_dir=None):
        """
        Saves dictionary as json file to specified location

        Parameters
        ----------
        d : dictionary
            object to save
        save_dir : str, default None
            location to save the data in case the class location is not desired
        """
        # Getting save path
        if save_dir == None:
            save_path = f"{self.save_dir}iaq_summary-{self.date.strftime('%Y-%m-%d')}.json"
        else:
            save_path = f"{save_dir}iaq_summary-{self.date.strftime('%Y-%m-%d')}.json"
        # saving as json to location
        with open(save_path, 'w') as f:
            json.dump(d, f)

    def run(self):
        """
        Calculates the summary statistics and saves the results to a file using all default values
        """
        res_dict = self.get_statistics()
        self.save(res_dict)

if __name__ == "__main__":
    """
    Calculates summary statistics and saves them to file
    """
    # System inputs if provided
    # -------------------------
    ## beacon number
    try:
        beacon = sys.argv[1]
    except IndexError:
        beacon = "00" # defaults if no argument provided
    ## save_dir
    try:
        save_dir = sys.argv[2]
    except IndexError:
        save_dir = "~/summary_data/" # defaults if no argument provided
    
    calculate = Calculate(beacon=beacon,save_dir=save_dir)
    calculate.run()