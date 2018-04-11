#!/usr/bin/python

import subprocess

class bluetoothHandler:

	def __init__(self):
		pass

	def start(self, mac_address):
		self.mac_address = mac_address

		print "start process ", self.mac_address
		self.ping = subprocess.Popen(['./multiple_ping.sh', '1c:66:aa:cc:9a:18'], bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		return self.ping

	def rssi(self):

		if not self.ping:
			self.start()

		print "ping ", self.mac_address

		rssi = subprocess.check_output(['hcitool', 'rssi', str(self.mac_address)])
		print rssi

		return rssi