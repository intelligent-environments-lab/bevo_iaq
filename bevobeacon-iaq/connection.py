import subprocess
import RPi.GPIO as GPIO
import time
import urllib

# setting up gpio
led_pin = 4 # gpio 4
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led_pin,GPIO.OUT)

while True:
    ps = subprocess.Popen(['iwconfig'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)
        print(output)
        GPIO.output(led_pin,GPIO.HIGH)
        status = "Connected"
    except subprocess.CalledProcessError:
        print(output)
        # grep did not match any lines
        GPIO.output(led_pin,GPIO.LOW)
        status = "Not Connected"

    print(status)
    time.sleep(5)

while True:
    try:
        url = "https://www.google.com"
        urllib.urlopen(url)
        status = "Connected"
    except:
        status = "Not connected"
    print(status)
    time.sleep(5)