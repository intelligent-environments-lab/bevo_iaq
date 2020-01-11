import busio
import adafruit_pcf8523
import time
import board
import urllib.request
from datetime import datetime

def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        print('connected')
        return True
    except:
        return False
 
myI2C = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_pcf8523.PCF8523(myI2C)
 
days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")

if connect():
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    y = datetime.now().year
    m = datetime.now().month
    d = datetime.now().day

    H = datetime.now().hour
    M = datetime.now().minute
    S = datetime.now().second

    t = datetime(y, m, d, H, M, S)
    #t = time.struct_time((y, m, d, H,  M,  S,    0,   -1,    -1))

    print("Setting time to:", t)     # uncomment for debugging
    rtc.datetime = t
    print()
    
while True:
    t = rtc.datetime
    #print(t)     # uncomment for debugging
 
    print("The date is %s %d/%d/%d" % (days[t.tm_wday], t.tm_mday, t.tm_mon, t.tm_year))
    print("The time is %d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec))
    
    time.sleep(1) # wait a second