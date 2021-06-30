# Bevo Beacon IAQ
This document details the basics of the Building EnVironment and Occupancy (BEVO) Beacon with enhanced Indoor Air Quality (IAQ) monitoring. 

## Installation

### 1. Install GIT and Clone Repository

Make sure your RPi is connected to WiFi. Then install git with

`$ sudo apt install git`

Clone this repository and `cd` into the newly created bevo `bevo_iaq` directory. Edit the `rpi_install.sh` file to include the correct GitHub credentials and set your timezone. 

### 2. Install Libraries to RPi

Run

`$ sh rpi_install.sh`

which will install updates, upgrade, install Python3, initialize the Tailscale VPN, and create a virtual environment. 

### 3. Install Libraries to Virtual Environment

Source the virtual environment with

`$ source .venv/bin/activate`

and then install the packages to operate the beacons IEQ monitoring capabilities

`pip install -r requirements.txt`

### 4. Enable Service Files on Boot

Finally, enable the service files by

`$ deactivate` (to get out of virtual environment)

`$ sh service_install.sh` 

and restart with `$ sudo reboot`!
