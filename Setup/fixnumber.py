import os

for i in range(0,51):
	if i < 10:
		i = '0' + str(i)
	#os.system(f'ssh pi@iaq{i} -o ConnectTimeout=3 \"echo {i} > ~/name\"')
	print(i)
	#os.system(f'ssh pi@iaq{i} -o ConnectTimeout=10 "sed \'s/beacon = \'00\'/beacon = \'{i}\'/g\' ~/bevo_iaq/Setup/Code/log_3.py"')
	os.system(f'scp -o ConnectTimeout=1 test.sh pi@iaq{i}:/home/pi/test.sh')
	os.system(f'ssh -o ConnectTimeout=1 pi@iaq{i} "sh /home/pi/test.sh {i}"')
	#os.system(f'ssh pi@iaq{i} -o ConnectTimeout=10 "sed \'s/beacon = \'00\'/beacon = \'{i}\'/g\' ~/bevo_iaq/Setup/Code/log_2.py"')
