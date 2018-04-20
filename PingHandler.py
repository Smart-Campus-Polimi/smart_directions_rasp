#!/usr/bin/python

import logging
import threading
import bluetoothHandler
import subprocess
import xml_parser
import thread_test
import csv

AVG_RATE = 20
filename_csv = 'test.csv'

f = open(filename_csv, 'w')

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
		if self.print_dir:
			logging.debug("print dir? %s", self.print_dir)
			self.oor_count += 1
			if self.oor_count > 1:
				self.engaged = False
				logging.debug("Out of range count: %s", self.oor_count)
				turn_off_projector(self)
				
def turn_off_projector(self):
	self.print_dir = False
	self.queue.put("turn off the projector")

	logging.info("Turn off the projector")		
	logging.info("User passes the destination")
	print "users pass the rasp, turn off proj"

def turn_on_projector(self, direct):
	print "ARROW", direct
	self.print_dir = True
	self.queue.put("turn on projector")
	logging.info("Printing out direction: ARROW %s", direct)

def user_in_range(self):
	self.position = check_proximity(self.rssi_avg)
	logging.debug("average rssi: %s", self.rssi_avg)
	logging.debug("position is %s", self.position)
	print "position:", self.position, "---", self.rssi_avg

	if self.position < 4:
		if not self.print_dir:
			turn_on_projector(self, self.direction)
						
		if self.position < 2:
			if not self.engaged:
				self.engaged = True
				logging.info("The user is engaged by rasp")
				if self.final:
					user_arrived(self)
					
		
	elif self.position > 3:
		if self.print_dir:
			turn_off_projector(self)
			logging.debug("Projector is off because position is %s and avg_rssi is %s", self.position, self.rssi_avg)



def user_arrived(self):
	logging.info("The user is in the final step")
	logging.info("sending stop messages to the other rasp")
	self.queue.put("user arrived "+ self.mac_target)

def create_csv(file, rssi, ping):
	file.write("\n"+str(rssi)+","+str(ping))	


class PingThread(threading.Thread):
	def __init__(self, user, root, queue):
		threading.Thread.__init__(self)
		self.user = user
		self.root = root
		self.queue = queue
		self.f = open(str(self)[19]+filename_csv, 'w')
		self.f.write("\"rssi\",\"ping\"")

	def run(self):
		self.mac_target = self.user['mac_address']
		self.place_id_target = self.user['place_id']
		self.timestamp_target = self.user['timestamp']
		logging.debug("Thread %s is running", self)
		logging.debug("Thread input params. mac: %s, place_id: %s, ts: %s", self.mac_target, self.place_id_target, self.timestamp_target)

		self.direction, self.final = xml_parser.find_direction(self.root, self.place_id_target, thread_test.rasp_id)
		logging.debug("parsing file. direcition: %s, is_final: %s", self.direction, self.final)
		logging.info("starting bluetooth handler")
		print "starting ping ... "

		bt = bluetoothHandler.bluetoothHandler()
		bt.start(self.mac_target)

		self.is_running, self.sum_rssi, self.count, self.rssi_avg, self.engaged, self.print_dir = initialize_values()
		logging.debug("setting up params. is_running %s, engaged %s", self.is_running, self.engaged)


		logging.info("staring while loop")
		while self.is_running:
			self.rssi, self.ping = bt.rssi()
			logging.debug("reading rssi: %s", self.rssi)

			if self.rssi is not None:
				if self.rssi == "OOR":
					logging.debug("out of range rssi: %s", self.rssi)
					user_out_of_range(self)
				else:
					try:
						self.rssi = float(self.rssi)
						self.rssi_avg, self.count, self.sum_rssi = average_rssi(self.rssi, self.count, self.sum_rssi)
						self.oor_count = 0
						create_csv(self.f, self.rssi, self.ping)
						#logging.debug("puntual rssi: %s", rssi)
					except ValueError as e:
						logging.error("Rssi concersion error %s", e)
						print "Conversion error!"
						continue

					if self.rssi_avg is not None:
						user_in_range(self)
	

	def stop(self):
		self.is_running = False
		f.close()

	