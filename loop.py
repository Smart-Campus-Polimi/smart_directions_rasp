import subprocess

while 1:
	try:
		rssi = subprocess.check_output(['hcitool', 'rssi', '1c:66:aa:cc:9a:18'])	 
		print rssi
	except subprocess.CalledProcessError as e:
		print e.output