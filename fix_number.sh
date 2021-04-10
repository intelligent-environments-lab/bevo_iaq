#!/bin/bash

str=$1

sed -i "s/beacon = '00'/beacon = '$str'/g" /home/pi/bevo_iaq/Setup/Code/log_3.py
sed -i "s/beacon = '00'/beacon = '$str'/g" /home/pi/bevo_iaq/Setup/Code/log_2.py
