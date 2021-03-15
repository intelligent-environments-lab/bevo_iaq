import serial

class DGS_NO2:
    def __init__(self) -> None:
        self.dgs = DGS
        pass
    
    def scan(self):
        '''
        Using serial connection, reads in values for T, RH, and NO2 concentration
        '''
        try:
            no2, t0, rh0 = self.dgs.take_measurement('/dev/ttyUSB0')
        except:
            no2 = -100
            t0 = -100
            rh0 = -100

        data = {'NO2':no2,'T_NO2':t0,'RH_NO2':rh0}
        return data

class DGS_CO:
    def __init__(self) -> None:
        self.dgs = DGS
        pass

    def scan(self):
        '''
        Using serial connection, reads in values for T, RH, and CO concentration
        '''
        try:
            co, t1, rh1 = self.dgs.take_measurement('/dev/ttyUSB1')
        except:
            # print('Error reading from CO sensor')
            co = -100
            t1 = -100
            rh1 = -100

        data = {'CO':co,'T_CO':t1,'RH_CO':rh1}
        return data

class DGS:
    @staticmethod
    def split(data):
        output = {
            'sn':data[0],
            'ppb':data[1],
            'temp':data[2],
            'rh':data[3],
            '_rawSensor':data[4],
            '_tempDigital':data[5],
            '_rhDigital':data[6],
            'day':data[7],
            'hour':data[8],
            'min':data[9],
            'sec':data[10],
        }
        return output

    @staticmethod
    def take_measurement(device, verbose=False):
        '''
        Uses the device string to read data from the serial DGS sensors
        Input:
            - device: string with the devices location - typically USB
        Returns:
            - c: concentration in ppb
            - tc: temperature in degress C
            - rh: relative humidity
        '''

        # Connecting to device
        ser = serial.Serial(device,timeout=5,write_timeout=5)

        # Getting data from device
        try:
            ser.write(b'\r')
            ser.write(b'\n\r')
            line = str(ser.readline(), 'utf-8')
            line = line[: -2]
            data = DGS.split(line.split(", "))

            # if verbose:
            #     # Outputting
            #     print("----------------------------")
            #     print(data)
            #     print("----------------------------")

            c = data['ppb']
            tc = data['temp']
            rh = data['rh']
            
        except:
            # if verbose:
            #     print('Timeout occurred during write')
            c = -100
            tc = -100
            rh = -100

        # Closing connection and returning relevant data
        ser.close()
        return c, tc, rh