import scd30
def scd30_scan(crc, pi, h):
    '''
    Measures the carbon dioxide concentration, temperature, and relative
    humidity in the room. Data are stored locally and to AWS S3 bucket.
    Returns a dictionary containing the carbon dioxide concentration in ppm,
    the temperature in degress Celsius, and the relative humidity as a 
    percent.
    '''

    # Declare all global variables to be returned
    global co2, tc, rh
    
    try:
        
        co2, tc, rh = scd30.calcCO2Values(pi,h,5)
        
    except:
        print('Problem opening connection to SCD30; saving dummy values')
        co2 = -100
        tc = -100
        rh = -100

    #pi.i2c_close(h)
    return {'CO2':co2,'TC':tc,'RH':rh}


crc_scd, pi_scd, h_scd = scd30.setupSensor()
print("SCD30 set up properly with")
print('  crc:',crc_scd)
print("  handle:",h_scd)
print("  pi:",pi_scd)
print(scd30_scan(crc_scd, pi_scd, h_scd))