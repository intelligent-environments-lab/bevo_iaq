from Setup.Code.log_2 import data_mgmt
import time
import pandas as pd
from adafruit import SGP30, TSL2591
from sensirion import SPS30, SCD30
from spec_dgs import DGS_NO2, DGS_CO
import management as mgmt

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

print(f"Successfully created: {sensors}")
print("Attempting scans")


while True:
    start_time = time.time()
    data = {}
    for name in sensors:
        print("\nScanning " + name)
        df = pd.DataFrame(
            [
                sensors[name].scan(),
                sensors[name].scan(),
                sensors[name].scan(),
                sensors[name].scan(),
                sensors[name].scan(),
            ]
        )
        print(df)
        data[name] = dict(df.mean())
        print(data[name])
    mgmt.data_mgmt(data)
    elapsed_time = time.time() - start_time
    print(elapsed_time)
    time.sleep(5)
    print("\n\n")

