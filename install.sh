#!/bin/bash

# Update package list
sudo apt-get update
sudo apt-get -y upgrade

# Additional apt packages
sudo apt-get install python3 -y
sudo apt-get install python3-pip -y
sudo apt-get install python3-venv -y
sudo apt-get install -y i2c-tools
sudo apt-get install -y libatlas-base-dev #for numpy
sudo apt-get install -y libopenjp2-7 #for display
sudo apt-get install -y libtiff5 #for display

# VPN
sudo apt-get install apt-transport-https
curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.gpg | sudo apt-key add -
curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt-get update
sudo apt-get install tailscale

# Github Credentials
git config --global user.email "hagenfritz@utexas.edu"
git config --global user.name "hagenfritz"

# Set up locale, timezone, language
sudo timedatectl set-timezone US/Central

for s in display sensors; do
	sudo cp startup/${s}.service /lib/systemd/system/${s}.service
 	sudo systemctl enable ${s}
done

sudo cp startup/bevobeacon.service /lib/systemd/system/bevobeacon.service
sudo systemctl enable bevobeacon
sudo systemctl start bevobeacon

# Virtual Environment Setup
rm -rf ~/bevo_iaq/.venv
mkdir ~/bevo_iaq/.venv
python3 -m venv ~/bevo_iaq/.venv
source ~/bevo_iaq/.venv/bin/activate

# Install additional packages
pip3 install -r ~/bevo_iaq/bevobeacon-iaq/requirements.txt
