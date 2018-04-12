#!/usr/bin/python

import subprocess

class bluetoothHandler:

	def __init__(self):
		pass

	def start(self, mac_address):
		self.mac_address = mac_address

		print "Thread", self," starts ping ", self.mac_address
		self.ping = subprocess.Popen(['unbuffer','./multiple_ping.sh', self.mac_address], bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		return self.ping

	def rssi(self):

		#start ping
		if not self.ping:
			self.start()

		#retrieve the ping line from stdout
		#line = self.ping.stdout.readline()

		#exit process if device is in range
		#if is_ping(line):
		try:
			#ask rssi
			rssi = subprocess.check_output(['hcitool', 'rssi', self.mac_address])#, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			return parse_rssi(rssi)
		except subprocess.CalledProcessError as e:
			#print e.output
			return None
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

#parse the rssi string
def parse_rssi(rssi):
	if (len(rssi)) < 19:
		return None
	elif len(rssi) == 20:
		return rssi[-1:]
	elif len(rssi) == 21:
		return rssi[-2:]
	elif len(rssi) == 22:
		return rssi[-3:]

	return None