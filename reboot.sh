#!/bin/bash
date >> /home/pi/log.txt
sudo echo "rebooting..." >> log.txt
sudo /bin/bash -c reboot