import time
import datetime
import board
import busio
import adafruit_tsl2591

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tsl2591.TSL2591(i2c)

dt = datetime.now()
filename = 'scd30_' + str(dt.year)+'-'+str(dt.month)+'-'+str(dt.day)+'_'+str(dt.hour)+'-'+str(dt.minute)+'-'+str(dt.second) + '.csv'
with open('Data/'+filename,'wt') as f:
  csv_writer = csv.writer(f)
  csv_writer.writerow(['date','time','total_light','infared','visible','full_spectrum'])

  while True:
    # Read and calculate the light level in lux.
    lux = sensor.lux
    print('Total light: {0}lux'.format(lux))
    # You can also read the raw infrared and visible light levels.
    # These are unsigned, the higher the number the more light of that type.
    # There are no units like lux.
    # Infrared levels range from 0-65535 (16-bit)
    infrared = sensor.infrared
    print('Infrared light: {0}'.format(infrared))
    # Visible-only levels range from 0-2147483647 (32-bit)
    visible = sensor.visible
    print('Visible light: {0}'.format(visible))
    # Full spectrum (visible + IR) also range from 0-2147483647 (32-bit)
    full_spectrum = sensor.full_spectrum
    print('Full spectrum (IR + visible) light: {0}'.format(full_spectrum))
    csv_writer.writerow([time.strftime('%m/%d/%y'),time.strftime('%H:%M:%S'),lux,infrared,visible,full_spectrum])
    time.sleep(1.0)
