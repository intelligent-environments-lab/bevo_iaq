#!/bin/bash

# Update package list
sudo apt-get update
sudo apt-get upgrade

# Install python 2 & 3
sudo apt-get install python
sudo apt-get install python3

# Install pip & pip3
sudo apt-get install python-pip -y # Python 2
sudo apt-get install python3-pip -y # Python 3
sudo pip3 install --upgrade setuptools

# Install pandas and numpy
sudo apt-get install python3-pandas -y
sudo apt-get install python3-numpy -y

# I2C Tools
sudo apt-get install -y python-smbus
sudo apt-get install -y i2c-tools

# Install other packages
sudo apt-get install python-pigpio -y

# Github Credentials
git config --global user.email "hagenfritz@utexas.edu"
git config --global user.name "hagenfritz"

# Replace pigpiod service file with bug free version
#install -o root -g root -m 0644 systemd/pigpiod.service /lib/systemd/system/pigpiod.service
#systemctl enable pigpiod
#systemctl start pigpiod

# Write environment file for environment variables
# *** CODE HERE ***

# Set up locale, timezone, language
sudo timedatectl set-timezone US/Central

# Install Hamachi
#sudo wget https://www.vpn.net/installers/logmein-hamachi_2.1.0.203-1_armhf.deb
#sudo dpkg -i logmein-hamachi_2.1.0.203-1_armhf.deb
sudo python3 hamachi_setup.py
#sudo rm -rf /var/lib/logmein-hamachi/
#sudo hamachi login
#hamachi set-nick
#hamachi attach hello@yoursite.com
#sudo update-rc.d logmein-hamachi defaults

# Sensor Libraries
sudo pip3 install adafruit-circuitpython-tsl2591
sudo pip3 install adafruit-circuitpython-sgp30
sudo apt-get install python-crcmod
sudo pip3 install pyserial

# AWS Libraries
sudo pip install boto3
sudo pip3 install boto3

# Reboot
sudo reboot
