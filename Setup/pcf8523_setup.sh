# Start by adding a device tree overlay:
#	In bash, type: 
#
#		sudo nano /boot/config.txt
#
#	In the file, add the following line to the bottom of the file:
#
#		dtoverlay=i2c-rtc,pcf8523
# Save and run
#
#	sudo reboot
# 
# Now check the i2c adresses with:
#
#	sudo i2cdetect -y 1
#
# Instead of 68, the device should now show up as UU

sudo apt-get -y remove fake-hwclock
sudo update-rc.d -f fake-hwclock remove
sudo systemctl disable fake-hwclock

# Now modify the original clock details:
#
#	sudo nano /lib/udev/hwclock-set
#
# And comment out the following lines:
#
#	if [ -e /run/systemd/system ] ; then
# 		exit 0
#	fi
# 
# As well as:
#
#	/sbin/hwclock --rtc=$dev --systz --badyear
# 
# And:
# 
# 	/sbin/hwclock --rtc=$dev --systz
#
# You can check the time from the RTC with:
#
#	sudo hwclock -D -r
# 
# To set the correct time, type:
# 
# 	sudo hwclock -w
#
# And then:
# 	
# 	sudo hwclock -r
# 
# Now the clock should be ready!
