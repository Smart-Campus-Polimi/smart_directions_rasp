#!/usr/bin/python

import logging
import threading
import bluetoothHandler
import subprocess
import xml_parser


AVG_RATE = 20


pwd = subprocess.check_output(['pwd']).rstrip() + "/"
rasp_id = subprocess.check_output(['cat', pwd+'config/raspi-number.txt'])[:1]


def average_rssi(rssi, count, sum_rssi):
		sum_rssi += rssi
		count += 1
		if count == AVG_RATE:
			rssi_avg = float(sum_rssi)/count
			count = 0
			sum_rssi = 0
			return rssi_avg, count, sum_rssi

		return None, count, sum_rssi

def check_proximity(rssi):
	if rssi > 0.5:
		position = "very very near"
		logging.info(position)
		return 0
	elif rssi > -1.0 and rssi <=0.5:
		position = "very near"
		logging.info(position)
		return 1
	elif rssi > -10 and rssi <=-1.0:
		position = "near"
		logging.info(position)
		return 2
	elif rssi > -20 and rssi <=-10:
		position = "visible"
		logging.info(position)
		return 3
	elif rssi <= -20:
		position = "in range"
		logging.info(position)
		return 4
	else:
		return 9


def initialize_values():
	return True, 0, 0, 0, False, False

def user_out_of_range(self):
		print "Out of Range"
		logging.info("Out of range")
		if self.engaged:
			logging.debug("Engaged? %s", self.engaged)
			self.oor_count += 1
			if self.oor_count > 1:
				self.print_dir = False
				logging.info("Turn off the projector")
				#turn_off()
				logging.info("User passes the destination")
				logging.debug("Out of range count: %s", self.oor_count)
				print "users pass the rasp, turn off proj"
				#if self.final:
				#	logging.info("Stopping all the ping")
				#	print "stop all the ping"
					#stop_all_process


def user_in_range(self):
	self.position = check_proximity(self.rssi_avg)
	logging.debug("average rssi: %s", self.rssi_avg)
	logging.debug("position is %s", self.position)
	print "position:", self.position, "---", self.rssi_avg

	if self.position < 4:
		if not self.print_dir:
			print "ARROW", self.direction
			self.print_dir = True
			logging.info("Printing out direction: ARROW %s", self.direction)
						
		if self.position < 2:
			if not self.engaged:
				self.engaged = True
				logging.info("The user is engaged by rasp")
		
	elif self.position > 3:
		if self.print_dir:
			self.print_dir = False
			logging.info("Turn off the projector")
			logging.debug("Projector is off because position is %s and avg_rssi is %s", self.position, self.rssi_avg)
			print "turn off the projector"

class PingThread(threading.Thread):
	def __init__(self, user, root):
		threading.Thread.__init__(self)
		self.user = user
		self.root = root

	def run(self):
		self.mac_target = self.user['mac_address']
		self.place_id_target = self.user['place_id']
		self.timestamp_target = self.user['timestamp']
		logging.debug("Thread %s is running", self)
		logging.debug("Thread input params. mac: %s, place_id: %s, ts: %s", self.mac_target, self.place_id_target, self.timestamp_target)

		self.direction, self.final = xml_parser.find_direction(self.root, self.place_id_target, rasp_id)
		logging.debug("parsing file. direcition: %s, is_final: %s", self.direction, self.final)
		logging.info("starting bluetooth handler")
		print "starting ping ... "

		bt = bluetoothHandler.bluetoothHandler()
		bt.start(self.mac_target)

		self.is_running, self.sum_rssi, self.count, self.rssi_avg, self.engaged, self.print_dir = initialize_values()
		logging.debug("setting up params. is_running %s, engaged %s", self.is_running, self.engaged)


		logging.info("staring while loop")
		while self.is_running:
			rssi = bt.rssi()
			logging.debug("reading rssi: %s", rssi)

			if rssi is not None:
				if rssi == "OOR":
					logging.debug("out of range rssi: %s", rssi)
					user_out_of_range(self)
				else:
					try:
						rssi = float(rssi)
						self.rssi_avg, self.count, self.sum_rssi = average_rssi(rssi, self.count, self.sum_rssi)
						self.oor_count = 0
						#logging.debug("puntual rssi: %s", rssi)
					except ValueError as e:
						logging.error("Rssi concersion error %s", e)
						print "Conversion error!"
						continue

					if self.rssi_avg is not None:
						user_in_range(self)
	

	def stop(self):
		self.is_running = False

	