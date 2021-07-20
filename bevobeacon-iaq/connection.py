import subprocess
import RPi.GPIO as GPIO
import time

# setting up gpio
led_pin = 4 # default to gpio 4
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led_pin,GPIO.OUT)

while True:
    ps = subprocess.Popen(['iwgetid'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)
        status = "Connected"
    except subprocess.CalledProcessError:
        # grep did not match any lines
        status = "Not Connected"

    print(status)
    if status == "Connected":
        GPIO.output(led_pin,GPIO.HIGH)
    else:
        GPIO.output(led_pin,GPIO.LOW)

    time.sleep(5)