import os

nickname = input('Name for this device on Hamachi VPN: ")

# Removing cloned configurations
os.system('sudo rm -rf /var/lib/logmein-hamachi/')

# Loigging in, setting nickname, and attaching
os.system('sudo hamachi login')
os.system('sudo hamachi set-nick '+ str(nickname))
os.system('sudo hamachi attach nagy@utexas.edu')

# Ensuring hamachi starts on power on
os.system('sudo update-rc.d logmein-hamachi defaults')
