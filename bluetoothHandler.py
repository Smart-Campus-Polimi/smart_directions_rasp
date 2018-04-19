#!/usr/bin/python

import subprocess
import logging

class bluetoothHandler:

	def __init__(self):
		pass

	def start(self, mac_address):
		self.mac_address = mac_address

		logging.basicConfig(filename= 'bluetooth_.log',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

		self.ping = subprocess.Popen(['unbuffer','./infinite_ping.sh', self.mac_address], bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		loggin.info("open infinite ping %s", self.ping)
		return self.ping

	def rssi(self):

		#start ping
		if not self.ping:
			self.start()

		#retrieve the ping line from stdout
		line = self.ping.stdout.readline()

		if not line:
			return None

		#check if is in range
		if is_range(line, self.mac_address):
			if is_ping(line, self.mac_address):
				rssi = parse_ping_rssi(line)
				logging.debug("rssi is %s", rssi)
				return rssi

			#else l2ping is establishing a new connection
			else:
				logging.debug("rssi is %s", line)
				return None
		else:
			#host out of range
			logging.info("device is out of range %s", line)
			return "OOR"
	

#check the ping reset
def is_ping(line, mac_addr):
	if "Ping" in line:
		logging.warning("ping in line  %s", line)
		return False
	elif "Connection reset" in line:
		logging.warning("connection reset  %s", line)
		return False
	elif "Read RSSI failed" in line:
		logging.warning("RSSI failed  %s", line)
		return False
	elif "loss" in line:
		logging.warning("something loss  %s", line)
		return False
	elif "Send failed" in line:
		logging.warning("Send failed  %s", line)
		return False
	elif "Recv Failed" in line:
		logging.warning("Recv failed  %s", line)
		return False

	return True

#check if device is out of range
def is_range(line, mac_addr):
	if "Host is down" in line:
		logging.warning("host is down %s", line)
		return False
	elif "no response" in line:
		logging.warning("no response %s", line)
		return False
	elif "l2ping" in line:
		logging.warning("l2ping %s", line)
		return False
	
	
	return True

#parse the ping string
def parse_ping_rssi(line):
	offset = line.find('RSSI') + 6
	line = line.replace('\n', '')
	rssi = line[offset:]
	ping = line[:(offset-13)]
	ping = ping[(ping.find('time')+4+1):]
	
	#print line, rssi, ping
	return rssi