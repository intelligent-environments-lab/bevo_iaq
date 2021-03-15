import time
import pandas as pd
from adafruit import SGP30, TSL2591
from sensirion import SPS30, SCD30
from spec_dgs import DGS_NO2, DGS_CO

sensors = {}
names = ['sgp','tsl','sps','scd','dgs_co','dgs_no2']
classes = [SGP30,TSL2591,SPS30,SCD30,DGS_CO,DGS_NO2]

for name, sens in zip(names,classes):
    try:
        sensor = sens()
        sensors.update({name:sensor})
    except:
        pass

print(f'Successfully created: {sensors}')
print('Attempting scans')

while True:
    start_time = time.time()
    for name in sensors:
        print('\nScanning '+name)
        df = pd.DataFrame([
            sensors[name].scan()
        ]*5)
        print(df)
        answer = dict(df.mean())
        print(answer)
    elapsed_time = time.time() - start_time
    print(elapsed_time)
    time.sleep(5)
    print('\n\n')
