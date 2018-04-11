#!/usr/bin/python

import subprocess

class bluetoothHandler:

	def __init__(self):
		pass

	def start(self, mac_address):
		self.mac_address = mac_address

		print "start process ", self.mac_address
		self.ping = subprocess.Popen(['./multiple_ping.sh', '1c:66:aa:cc:9a:1a'], bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		return self.ping

	def rssi(self):

		if not self.ping:
			self.start()

		print "ping ", self.mac_address

		sum_rssi = 0
		count = 0  
		#while True:

		try:
			rssi = subprocess.check_output(['hcitool', 'rssi', "1c:66:aa:cc:9a:1a"])#, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		except subprocess.CalledProcessError as e:
			print e.output

		#print "questo rssi", int(rssi)
			#sum_rssi += int(rssi[-2:])
			#count += count 

			#if count == 50:
			#	avg_rssi = float(sum_rssi/count)
			#	count = 0
			#	sum_rssi = 0
			

		return rssi