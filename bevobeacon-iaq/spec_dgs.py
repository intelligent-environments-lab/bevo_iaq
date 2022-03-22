"""Spec DGS Sensors

This script handles data measurements from the CO and NO2 Digital Gas Sensors
made by SPEC.
"""

import numpy as np
import serial
import asyncio


class DGS:
    def __init__(self, port) -> None:
        """
        Create and config the Serial object for connecting to the spec
        dgs sensors
        """
        ser = serial.Serial()
        ser.port = port
        ser.timeout = 1
        ser.write_timeout = 1
        self.ser = ser

    @staticmethod
    def split(data):
        """Sort and label the measured data"""
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
        Parameters
        ----------
        device: str
            devices location - typically USB

        Returns
        -------
        c: float
            concentration in ppb
        tc: float
            temperature in degress C
        rh: float
            relative humidity in percent
        """

        ser = self.ser
        # Connecting to device
        ser.open()

        # Getting data from device
        try:
            # b"\r" is the command to read one measurement from the sensor
            ser.write(b"\r")
            ser.write(b"\r")  # Repeat to make sure the sensor recieves it

            await asyncio.sleep(0.1)  # Wait for response

            # Read and decode data
            line = str(ser.readline(), "utf-8")
            line = line[:-2]
            data = DGS.split(line.split(", "))

            c = data["ppb"]
            tc = data["temp"]
            rh = data["rh"]

        except:
            c = np.nan
            tc = np.nan
            rh = np.nan

        # Close connection (also clears queue) and return relevant data
        ser.close()
        return float(c), float(tc), float(rh)


class DGS_NO2(DGS):
    def __init__(self) -> None:
        super().__init__("/dev/ttyUSB0")

    async def scan(self):
        """
        Using serial connection, reads in values for T, RH, and NO2 concentration
        """
        try:
            no2, t0, rh0 = await self.take_measurement()
        except:
            no2 = np.nan
            t0 = np.nan
            rh0 = np.nan

        data = {"nitrogen_dioxide-ppb": no2, "t_from_no2-c": t0, "rh_from_no2-percent": rh0}
        return data


class DGS_CO(DGS):
    def __init__(self) -> None:
        super().__init__("/dev/ttyUSB1")

    async def scan(self):
        """
        Using serial connection, reads in values for T, RH, and CO concentration
        """
        try:
            co, t1, rh1 = await self.take_measurement()
        except:
            co = np.nan
            t1 = np.nan
            rh1 = np.nan

        data = {"carbon_monoxide-ppb": co, "t_from_co-c": t1, "rh_from_co-percent": rh1}
        return data
