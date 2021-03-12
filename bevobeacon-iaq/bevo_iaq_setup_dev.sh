#!/bin/bash

# Update package list
sudo apt-get update
sudo apt-get upgrade

# Additional apt packages
sudo apt-get install python3 -y
sudo apt-get install python3-pip -y
sudo apt-get install python3-venv -y
sudo apt-get install -y i2c-tools
sudo apt-get install libatlas-base-dev #for numpy

# Virtual Environment Setup
rm -rf ~/bevo_iaq/.venv
mkdir ~/bevo_iaq/.venv
python3 -m venv ~/bevo_iaq/.venv
source ~/bevo_iaq/.venv/bin/activate

# Install addtional packages
pip install -r Setup/requirements.txt

# Github Credentials
git config --global user.email "hagenfritz@utexas.edu"
git config --global user.name "hagenfritz"

# Set up locale, timezone, language
sudo timedatectl set-timezone US/Central
