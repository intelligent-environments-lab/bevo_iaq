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

for name in sensors:
    print('Scanning '+name)
    print(sensors[name].scan)
