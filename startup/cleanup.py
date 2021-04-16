
import os

class clean():
    def remove_old_services(self):
        """disables and removes old service files"""
        for service in ["sensirion","adafruit","pigpio","hamachi"]:
            # disabling
            os.system(f"sudo systemctl disable {service}.service")
            # looking in two directories for services to remove
            os.system(f"sudo rm /etc/systemd/system/{service}.service")
            os.system(f"sudo rm /lib/systemd/system/{service}.service")

    def update_from_git(self):
        """pulls from git"""
        os.system("cd ~/bevo_iaq && git reset --hard && git pull")

    def install_new_software(self):
        """runs the installation"""
        os.system("cd ~/bevo_iaq/ && sh install.sh")

    def update_beacon_number(self):
        """updates the beacon number from user prompt"""
        bb = input("Beacon Number (include zero for numbers less than 10): ")
        os.system(f"cd ~/bevo_iaq/ $$ sh fix_number.sh {bb}")

    def run(self):
        """runs all the functions with"""
        print("REMOVING OLD SERVICE FILES")
        self.remove_old_services()
        #print("UPDATING FROM GIT")
        #self.update_from_git()
        print("INSTALLING NEW SOFTWARE")
        self.install_new_software()
        print("UPDATING BEACON NUMBER")
        self.update_beacon_number()
        print("REBOOTING")
        os.system("sudo reboot")

def main():
    c = clean()
    c.run()

if __name__ == '__main__':
    main()
