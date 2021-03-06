#!/usr/bin/python

import threading
import BluetoothHandler
import xml_parser
import my_main
import csv
from datetime import datetime
from collections import namedtuple
import constants as c

AVG_RATE = 20

ProjMsg = namedtuple('ProjMsg', ['mac_address', 'direction', 'proj_status', 'final_pos', 'timestamp'])


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
		c.logging.info(position)
		return 0
	elif rssi > -1.0 and rssi <=0.5:
		position = "very near"
		c.logging.info(position)
		return 1
	elif rssi > -10 and rssi <=-1.0:
		position = "near"
		c.logging.info(position)
		return 2
	elif rssi > -20 and rssi <=-10:
		position = "visible"
		c.logging.info(position)
		return 3
	elif rssi <= -20:
		position = "in range"
		c.logging.info(position)
		return 4
	else:
		return 9

def _initialize_values():
	return True, 0, 0, 0, False, False

def user_out_of_range(self):
		print self.mac_target, " -> Out of Range"
		c.logging.info("Out of range")
		if self.print_dir:
			c.logging.debug("print dir? %s", self.print_dir)
			self.oor_count += 1
			if self.oor_count > 1:
				self.engaged = False
				c.logging.debug("Out of range count: %s", self.oor_count)
				turn_off_projector(self)
				
def is_near(self):
	self.print_dir = False
	p_msg = ProjMsg(mac_address=self.mac_target, direction=self.direction, proj_status=self.print_dir, final_pos=False, timestamp=datetime.now())
	
	c.logging.debug("Projector msg: %s", p_msg)
	c.logging.info("Putting in queue the proj_msg")

	self.queue.put(p_msg)
	

def is_out_of_range(self, direct):
	self.print_dir = True
	p_msg = ProjMsg(mac_address=self.mac_target, direction=self.direction, proj_status=self.print_dir, final_pos=False, timestamp=datetime.now())
	
	c.logging.debug("Direction: ARROW %s", direct)
	c.logging.debug("Projector msg: %s", p_msg)
	c.logging.info("Putting in queue the proj_msg")
	self.queue.put(p_msg)
	


def user_in_range(self):
	self.position = check_proximity(self.rssi_avg) #converte rssi in valori da 0 a 5 (0 vicinissimo, 5 lontano)
	c.logging.debug("average rssi: %s", self.rssi_avg)
	c.logging.debug("position is %s", self.position)
	print self.mac_target, "-> position:", self.position, "---", self.rssi_avg

	if self.position < 4:
		if not self.print_dir:
			is_near(self)
						
		if self.position < 2:

			if not self.engaged:
				self.engaged = True
				c.logging.info("The user is engaged by rasp")
				#if self.final:
				#when an user is engaged by the sniffer, every sniffer sends a msg. then if the sniffer itself is the final one the main handle this
				user_arrived(self)
					
		
	elif self.position > 3:
		if self.print_dir:
			is_out_of_range(self)
			c.logging.debug("Projector is off because position is %s and avg_rssi is %s", self.position, self.rssi_avg)



def user_arrived(self):
	p_msg = ProjMsg(mac_address=self.mac_target, direction=self.direction, proj_status=self.print_dir, final_pos=self.final, timestamp=datetime.now())
	self.queue.put(p_msg)
	c.logging.info("Putting in queue the proj_msg with final purpose")
	c.logging.debug("Projector msg: %s", p_msg)

def create_csv(file, mac_addr, rssi, ping, ts):
	file.write("\n"+str(mac_addr)+","+str(rssi)+","+str(ping)+","+str(ts))	


class PingThread(threading.Thread):
	def __init__(self, user, root, queue, stop_queue):
		threading.Thread.__init__(self)
		self.user = user #mac address + posto + id + flag... ecc (json)
		self.root = root #root xml
		self.queue = queue #coda c'e/non c'e
		self.stop_queue = stop_queue #per farlo stoppare
		#filename_csv = main.ping_csv_path
		self.thread_number = str(self)[19:21] #id del thread

		try:
			int(self.thread_number[1])
		except ValueError:
			self.thread_number=self.thread_number[0]
			
		#self.f = open(filename_csv +"/thread_"+ self.thread_number +".csv", 'w')
		#self.f.write("\"mac_address\",\"rssi\",\"ping\",\"timestamp\"")

	def run(self):
		self.mac_target, self.place_id_target, __, self.timestamp_target, __, __ = self.user
		
		c.logging.debug("Thread %s is running", self)
		c.logging.debug("Thread input params. mac: %s, place_id: %s, ts: %s", self.mac_target, self.place_id_target, self.timestamp_target)

		self.direction, self.final = xml_parser.find_direction(self.root, self.place_id_target, c.RASP_ID) #dove devo andare
		c.logging.debug("parsing file. direcition: %s, is_final: %s", self.direction, self.final)
		c.logging.info("starting bluetooth handler")
		print "starting ping ... ", self.mac_target

		self.bt = BluetoothHandler.BluetoothHandler() #modulo per ping
		self.bt.start(self.mac_target) #starta il ping 

		self.is_running, self.sum_rssi, self.count, self.rssi_avg, self.engaged, self.print_dir = _initialize_values()
		c.logging.debug("setting up params. is_running %s, engaged %s", self.is_running, self.engaged)


		c.logging.info("staring while loop")
		#per stoppare
		while self.is_running:
			#TODO method
			if not self.stop_queue.empty():
				self.msg = self.stop_queue.get()
				print "stop msg", self.msg
				c.logging.info("A new message is received")
				c.logging.debug("Msg info %s", self.msg)
				
				if type(self.msg).__name__ == "StopMsg": #stop queue ha self.msg
					c.logging.info("The message is a StopMsg")
					self.stop_mac_addr, __ = self.msg #estrare da stop queue il mac da stoppare
					if self.stop_mac_addr == self.mac_target:
						self.stop() #stoppo il thread


			#per guardare rssi
			self.rssi, self.ping = self.bt.rssi() #self.ping = rtt

			if self.rssi is not None:
				if self.rssi == "OOR":
					c.logging.debug("out of range rssi: %s", self.rssi)
					user_out_of_range(self)
				else:
					try:
						self.rssi = float(self.rssi)
					except ValueError as e:
						c.logging.error("Rssi concersion error %s", e)
						print "Conversion error!"
						continue

					self.rssi_avg, self.count, self.sum_rssi = average_rssi(self.rssi, self.count, self.sum_rssi) #una volta su AVG RATE ritorna il valore, le altre volte NONE
					self.oor_count = 0
					#create_csv(self.f, self.mac_target, self.rssi, self.ping, datetime.now())

					if self.rssi_avg is not None:
						user_in_range(self)
				

	def stop(self):
		c.logging.info("Closing the thread")
		self.is_running = False #stoppa il thread
		self.bt.stop_proc()
		#self.f.close()

	
