#!/usr/bin/python

import subprocess
import logging
import constants as c

class BluetoothHandler:

	def __init__(self):
		pass

	def start(self, mac_address):
		self.mac_address = mac_address

		self.ping = subprocess.Popen(['unbuffer', c.PWD+'config/infinite_ping.sh', self.mac_address], bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		c.logging.info("open infinite ping %s", self.ping)
		return self.ping

	def rssi(self):
		#start ping
		if not self.ping:
			self.start()

		#retrieve the ping line from stdout
		line = self.ping.stdout.readline()

		if not line:
			return None, None

		#check if is in range
		if self._is_range(line, self.mac_address):
			if self._is_ping(line, self.mac_address):
				rssi, ping = self._parse_ping_rssi(line)
				c.logging.debug("rssi is %s", rssi)
				return rssi, ping

			#else l2ping is establishing a new connection
			else:
				c.logging.debug("rssi is %s", line)
				return None, None
		else:
			#host out of range
			c.logging.info("device is out of range %s", line)
			return "OOR", None
	

	def stop_proc(self):
		c.logging.info("Terminate thread infinite ping")
		print "terminate thread ping"
		self.ping.terminate()

	#check the ping reset
	def _is_ping(self, line, mac_addr):
		if "Ping" in line:
			c.logging.debug("ping in line  %s", line)
			return False
		elif "Connection reset" in line:
			c.logging.debug("connection reset  %s", line)
			return False
		elif "Read RSSI failed" in line:
			c.logging.debug("RSSI failed  %s", line)
			return False
		elif "loss" in line:
			c.logging.debug("something loss  %s", line)
			return False
		elif "Send failed" in line:
			c.logging.debug("Send failed  %s", line)
			return False
		elif "Recv Failed" in line:
			c.logging.debug("Recv failed  %s", line)
			return False
		elif "Connection timed" in line:
			c.logging.debug("connection timed out  %s", line)
			return False

		return True

	#check if device is out of range
	def _is_range(self, line, mac_addr):
		if "Operation now" in line:
			c.logging.warning("l2ping problem %s", line)
			print "L2ping problem"
			return False
		if "Host is down" in line:
			c.logging.debug("host is down %s", line)
			return False
		elif "no response" in line:
			c.logging.debug("no response %s", line)
			return False
		elif "l2ping" in line:
			c.logging.debug("l2ping %s", line)
			return False
		
		
		return True

	#parse the ping string
	def _parse_ping_rssi(self, line):
		offset = line.find('RSSI') + 6
		line = line.replace	('\n', '')
		rssi = line[offset:]
		ping = line[:(offset-13)]
		ping = ping[(ping.find('time')+4+1):]
		
		return rssi, ping

