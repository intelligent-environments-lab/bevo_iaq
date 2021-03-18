import time
import asyncio

import pandas as pd
from adafruit import SGP30, TSL2591
from sensirion import SPS30, SCD30
from spec_dgs import DGS_NO2, DGS_CO
import management as mgmt



async def main():
    sensor_classes = {
        "sgp": SGP30,
        "tsl": TSL2591,
        "sps": SPS30,
        "scd": SCD30,
        "dgs_co": DGS_CO,
        "dgs_no2": DGS_NO2,
    }

    sensors = {}

    for name, sens in sensor_classes.items():
        try:
            sensor = sens()
            sensors.update({name: sensor})
        except:
            pass
    
    manually_enabled_sensors = list(set(sensors) & set(['tsl','sps','scd']))
    time.sleep(1)
    print(f"Successfully created: {sensors}")
    print("Attempting scans")
    
    starttime = time.time()
    loop = True
    while loop:
        start_time = time.time()
        data = {}
        #for name in sensors:
        async def scan(name):
            df = pd.DataFrame(
                [
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                    await sensors[name].scan(),
                ]
            )
            print("\nScan results for " + name)
            print(df)
            data[name] = dict(df.median())
            print(data[name])

        for manual_sensor in manually_enabled_sensors:
            try:
                sensors[manual_sensor].enable()
                sensors[manual_sensor].enable()
            except:
                pass

        time.sleep(0.1)

        await asyncio.gather(*[scan(name) for name in sensors])

        for manual_sensor in manually_enabled_sensors:
            try:
                sensors[manual_sensor].disable()
                sensors[manual_sensor].disable()
            except:
                pass

        mgmt.data_mgmt(data)
        elapsed_time = time.time() - start_time
        print(elapsed_time)
        time.sleep(1)
        #time.sleep(60.0 - ((time.time() - starttime) % 60.0))
        print("\n\n")
        # loop = False

if __name__ == '__main__':
    asyncio.run(main())