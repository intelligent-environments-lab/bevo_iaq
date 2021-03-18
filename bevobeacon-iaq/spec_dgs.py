import numpy as np
import serial
import asyncio

class DGS:
    def __init__(self, port) -> None:
        ser = serial.Serial()
        ser.port = port
        ser.timeout = 1
        ser.write_timeout = 1
        self.ser = ser

    @staticmethod
    def split(data):
        output = {
            "sn": data[0],
            "ppb": data[1],
            "temp": data[2],
            "rh": data[3],
            "_rawSensor": data[4],
            "_tempDigital": data[5],
            "_rhDigital": data[6],
            "day": data[7],
            "hour": data[8],
            "min": data[9],
            "sec": data[10],
        }
        return output

    async def take_measurement(self, verbose=False):
        """
        Uses the device string to read data from the serial DGS sensors
        Input:
            - device: string with the devices location - typically USB
        Returns:
            - c: concentration in ppb
            - tc: temperature in degress C
            - rh: relative humidity
        """

        ser = self.ser
        # Connecting to device
        ser.open()

        # Getting data from device
        try:
            ser.write(b"\r")
            ser.write(b"\r")
            await asyncio.sleep(0.1)
            line = str(ser.readline(), "utf-8")
            line = line[:-2]
            data = DGS.split(line.split(", "))

            # if verbose:
            #     # Outputting
            #     print("----------------------------")
            #     print(data)
            #     print("----------------------------")

            c = data["ppb"]
            tc = data["temp"]
            rh = data["rh"]

        except:
            # if verbose:
            #     print('Timeout occurred during write')
            c = np.nan
            tc = np.nan
            rh = np.nan

        # Closing connection and returning relevant data
        ser.close()
        return float(c), float(tc), float(rh)


class DGS_NO2(DGS):
    def __init__(self) -> None:
        super().__init__("/dev/ttyUSB0")

    async def scan(self):
        """
        Using serial connection, reads in values for T, RH, and NO2 concentration
        """

        # print('no2 scan start')
        try:
            no2, t0, rh0 = await self.take_measurement()
        except:
            no2 = np.nan
            t0 = np.nan
            rh0 = np.nan
        # print('no2 scan end')
         
        data = {"NO2": no2, "T_NO2": t0, "RH_NO2": rh0}
        return data


class DGS_CO(DGS):
    def __init__(self) -> None:
        super().__init__("/dev/ttyUSB1")

    async def scan(self):
        """
        Using serial connection, reads in values for T, RH, and CO concentration
        """
        # print('co scan start')

        try:
            co, t1, rh1 = await self.take_measurement()
        except:
            # print('Error reading from CO sensor')
            co = np.nan
            t1 = np.nan
            rh1 = np.nan
        # print('co scan end')
        data = {"CO": co, "T_CO": t1, "RH_CO": rh1}
        return data

