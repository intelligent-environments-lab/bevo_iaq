# Bevo Beacon IAQ
This document details the basics of the Building EnVironment and Occupancy (BEVO) Beacon with enhanced Indoor Air Quality (IAQ) monitoring. 

## Installation

Make sure your RPi is connected to WiFi. Then install git with

`$ sudo apt install git`

Clone this repository and `cd` into the newly created bevo `bevo_iaq` directory. Edit the `rpi_install.sh` file to include the correct GitHub credentials and set your timezone. After, run

`$ sh rpi_install.sh`

which will install updates, upgrade, install Python3, initialize the Tailscale VPN, and create a virtual environment. Source the virtual environment with

`$ source .venv/bin/activate`

and then install the packages to operate the beacons IEQ monitoring capabilities

`pip install -r requirements.txt`

Finally, enable the service files by

`$ deactivate` (optional)
`$ sh startup/service_install.sh`

and restart with `$ sudo reboot`!
