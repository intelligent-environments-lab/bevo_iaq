import numpy as np

import sps30
import scd30

class SPS30:
    def __init__(self) -> None:
        pass

    def scan(self):
        '''
        Measures different particulate matter counts and concentrations in the
        room. Data are stored locally and to AWS S3 bucket.
        Returns dictionary containing counts for 0.5, 1, 2.5 , 4, and 10 microns
        in diameter and concentrations for 1, 2.5, 4, and 10 microns in diameter.
        '''
        try:
            pm_n, pm_c = sps30.takeMeasurement()
        except:
            pm_n = [np.nan,np.nan,np.nan,np.nan,np.nan]
            pm_c = [np.nan,np.nan,np.nan,np.nan]

        return {'pm_n_0p5':pm_n[0],'pm_n_1':pm_n[1],'pm_n_2p5':pm_n[2],'pm_n_4':pm_n[3],'pm_n_10':pm_n[4],'pm_c_1':pm_c[0],'pm_c_2p5':pm_c[1],'pm_c_4':pm_c[2],'pm_c_10':pm_c[3]}


class SCD30:
    def __init__(self) -> None:
        pass
    
    def scan(self):
        '''
        Measures the carbon dioxide concentration, temperature, and relative
        humidity in the room. Data are stored locally and to AWS S3 bucket.
        Returns a dictionary containing the carbon dioxide concentration in ppm,
        the temperature in degress Celsius, and the relative humidity as a 
        percent.
        '''

        try:
            tc, rh, co2 = scd30.takeMeasurement()
        except:
            co2 = np.nan
            tc = np.nan
            rh = np.nan

        return {'CO2':co2,'TC':tc,'RH':rh}
