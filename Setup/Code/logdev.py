from busio import I2C

class BevoBeacon:
    def __init__(self,beacon) -> None:
        self.beacon = beacon
        self.i2c = I2C(SCL, SDA)

        try:
            sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
            sgp30.iaq_init()
        except ValueError:
    	    print("No device")

        self.filepath = {'adafruit':'/home/pi/DATA/adafruit/'}

    def filename(self, date):
        return self.filepath['adafruit'] + 'b' + self.beacon + '_' + date.strftime('%Y-%m-%d') + '.csv'

    def sgp30_scan(sgp30):
        # Declare all global variables for use outside the functions
        global eCO2, TVOC
        try:
            # Retrieve sensor scan data
            eCO2, TVOC = sgp30.iaq_measure()
        except:
            print('Error reading from SGP30')
            eCO2 = -100
            TVOC = -100

        # Outputting
        if verbose:
            print("-------------------------")
            print("TVOC (ppb):\t"+str(TVOC))
            print("eCO2 (ppm):\t"+str(eCO2))
            print("-------------------------")
        # Return data
        data = {'TVOC': TVOC, 'eCO2': eCO2}
        return data


def main():
    beacon = BevoBeacon()


    while True:
        sgp_data_old = {'TVOC': 0, 'eCO2': 0}
        for j in range(5):
            #print('Running SGP30 scan...')
            try:
                sgp_data_new = sgp30_scan(sgp30)
                if sgp_data_new['TVOC'] != -100 and math.isnan(sgp_data_new['TVOC']) == False:
                    sgp_count += 1
                    for x in sgp_data_old:
                        sgp_data_old[x] += sgp_data_new[x]
            except Exception as inst:
                print(inst)
        
        for x in sgp_data_old:
            try:
                sgp_data_old[x] /= sgp_count
            except ZeroDivisionError:
                sgp_data_old[x] = np.nan
        
        print("TVOC (ug/m3): {0:.3f}".format(sgp_data_old['TVOC']))

main()