import dgs

class DGS_NO2:
    def __init__(self) -> None:
        pass
    
    def scan(self):
        '''
        Using serial connection, reads in values for T, RH, and NO2 concentration
        '''
        try:
            no2, t0, rh0 = dgs.takeMeasurement('/dev/ttyUSB0')
        except:
            no2 = -100
            t0 = -100
            rh0 = -100

        data = {'NO2':no2,'T_NO2':t0,'RH_NO2':rh0}
        return data

class DGS_CO:
    def __init__(self) -> None:
        pass

    def scan(self):
        '''
        Using serial connection, reads in values for T, RH, and CO concentration
        '''
        try:
            co, t1, rh1 = dgs.takeMeasurement('/dev/ttyUSB1')
        except:
            print('Error reading from CO sensor')
            co = -100
            t1 = -100
            rh1 = -100

        data = {'CO':co,'T_CO':t1,'RH_CO':rh1}
        return data