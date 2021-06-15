#!/bin/bash
date >> /home/pi/log.txt
echo "rebooting..." >> log.txt
sudo /bin/bash -c reboot