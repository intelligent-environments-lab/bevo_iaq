#!/bin/bash

str=$1

sed -i "s/beacon = '00'/beacon = '$str'/g" /home/pi/bevo_iaq/bevobeacon-iaq/main.py
sed -i "s/beacon = '00'/beacon = '$str'/g" /home/pi/bevo_iaq/bevobeacon-iaq/management.py
