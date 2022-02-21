[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub top language](https://img.shields.io/github/languages/top/intelligent-environments-lab/bevo_iaq)

# Bevo Beacon IAQ
This document details the basics of the Building EnVironment and Occupancy (BEVO) Beacon with enhanced Indoor Air Quality (IAQ) monitoring. 

## Installation

### 1. Install GIT and Clone Repository

Make sure your RPi is connected to WiFi. Then install git with

```bash
sudo apt install git
```

Clone this repository and `cd` into the newly created bevo `bevo_iaq` directory. Edit the `rpi_install.sh` file to include the correct GitHub credentials and set your timezone. 

### 2. Install Libraries to RPi

Run

```bash
sh rpi_install.sh
```

which will install updates, upgrade, install Python3, initialize the Tailscale VPN, and create a virtual environment. 

### 3. Install Libraries to Virtual Environment

Create a virtual environment with

```bash
source .venv/bin/activate
```

and then install the packages to operate the beacon's monitoring capabilities

```bash
pip install -r requirements.txt
```

### 4. Enable Service Files on Boot

Finally, enable the service files by

```bash
deactivate
```

```bash
sh service_install.sh
```

### 5. Specify Device Number (Optional)

By default, the device number is 00. You can specify the number by running the `fix_number` shell script:

```bash
sh fix_number.sh <label>
```

where `<label>` is any identifier you would like whether it be numeric, alphabetical, or a combination.

### 6. Finalize and Check

Simply restart with `$ sudo reboot` for a clean start to the device.

You can check if the device is working properly by examining the data in the `DATA` directory or on the individual services with:

```bash
sudo journalctl -u <service_name>.service
```

