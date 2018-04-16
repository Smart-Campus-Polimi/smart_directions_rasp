#!/usr/bin/python

import subprocess

class bluetoothHandler:

	def __init__(self):
		pass

	def start(self, mac_address):
		self.mac_address = mac_address

		print "Object", self," starts ping ", self.mac_address
		self.ping = subprocess.Popen(['unbuffer','./infinite_ping.sh', self.mac_address], bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		return self.ping

	def rssi(self):

		#start ping
		if not self.ping:
			self.start()

		#retrieve the ping line from stdout
		line = self.ping.stdout.readline()

		#exit process if device is in range
		if is_ping(line):
			rssi = parse_ping_rssi(line)
			return rssi
		else:
			return None
		#try:
			#ask rssi
		#	rssi = subprocess.check_output(['hcitool', 'rssi', self.mac_address], stderr=subprocess.STDOUT)
		#	return parse_rssi(rssi)
		#except subprocess.CalledProcessError as e:
			#print e.output
		#	return None
		#else:
		#	return None



#check if ping is working == device is in range or mac address is correct
def is_ping(line):
	if not line:
		return False
	elif "Ping" in line:
		return False
	elif "Host is down" in line:
		return False
	elif "Send failed" in line:
		return False
	elif "Recv failed" in line:
		return False
	elif "no response" in line:
		return False
	elif "l2ping" in line:
		return False
	elif "Oops" in line:
		return False

	return True

#parse the ping string
def parse_ping_rssi(line):
	offset = line.find('RSSI') + 6
	line = line.replace('\n', '')
	rssi = line[offset:]
	print line, rssi