# Setting up system service files
for s in display sensors; do
	sudo cp ~/bevo_iaq/services/${s}.service /lib/systemd/system/${s}.service
 	sudo systemctl enable ${s}
done

sudo cp ~/bevo_iaq/services/bevobeacon.service /lib/systemd/system/bevobeacon.service
sudo systemctl enable bevobeacon
sudo systemctl start bevobeacon
