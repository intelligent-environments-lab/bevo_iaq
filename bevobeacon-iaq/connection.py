import subprocess
import RPi.GPIO as GPIO
import time

# setting up gpio
led_pin = 4 # gpio 4
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led_pin,GPIO.OUT)

while True:
    ps = subprocess.Popen(['iwconfig'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)
        GPIO.output(led_pin,GPIO.HIGH)
    except subprocess.CalledProcessError:
        # grep did not match any lines
        GPIO.output(led_pin,GPIO.LOW)

    time.sleep(5)