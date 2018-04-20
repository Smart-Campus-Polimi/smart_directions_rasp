#!/usr/bin/python

import threading
import signal
import time
import sys
import json
import getopt
import Queue
import subprocess
import bluetoothHandler
import xml_parser
import logging
import xml.etree.ElementTree as ET
import pprint as pp
import MqttHandler

AVG_RATE = 20


pwd = subprocess.check_output(['pwd']).rstrip() + "/"
rasp_id = subprocess.check_output(['cat', pwd+'config/raspi-number.txt'])[:1]
logging.basicConfig(filename= 'rasp'+rasp_id+'.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug("Start smart directions on rasp "+rasp_id)
logging.debug("directory: "+ pwd)

broker_address = "10.0.2.15" 
broker_address_cluster = "192.168.1.74"
topic_name = "topic/rasp4/directions"


class PingThread(threading.Thread):
	def __init__(self, user):
		threading.Thread.__init__(self)
		self.user = user

	def run(self):
		mac_target = self.user['mac_address']
		place_id_target = self.user['place_id']
		timestamp_target = self.user['timestamp']
		logging.debug("Thread %s is running", self)
		logging.debug("Thread input params. mac: %s, place_id: %s, ts: %s", mac_target, place_id_target, timestamp_target)

		logging.info("Opening map")
		tree = ET.parse('map.xml')
		root = tree.getroot()

		direction, final = xml_parser.find_direction(root, place_id_target, rasp_id)
		logging.debug("parsing file. direcition: %s, is_final: %s", direction, final)
		logging.info("starting bluetooth handler")
		print "starting ping ... "

		bt = bluetoothHandler.bluetoothHandler()
		bt.start(mac_target)
		self.is_running = True
		sum_rssi = 0 
		count = 0
		rssi_avg = 0
		arrived = False
		oor_count = 0
		print_dir = False

		logging.debug("setting up params. is_running %s, arrived %s", self.is_running, arrived)
		logging.info("staring while loop")
		while self.is_running:
			rssi = bt.rssi()
			logging.debug("reading rssi: %s", rssi)


			if rssi is not None:
				if rssi == "OOR":
					print "Out of Range"
					logging.info("Out of range")
					logging.debug("out of range rssi: %s", rssi)
					print_dir = False
					if arrived:
						logging.debug("Arrived? %s", arrived)
						oor_count += 1
						if oor_count > 2:
							logging.info("User passes the destination")
							logging.debug("Out of range count: %s", oor_count)
							print "users pass the destination"
							if final:
								logging.info("Stopping all the ping")
								print "stop all the ping"
								#todo!
				else:
					try:
						rssi = float(rssi)
						rssi_avg, count, sum_rssi = average_rssi(rssi, count, sum_rssi)
						#logging.debug("puntual rssi: %s", rssi)
					except ValueError as e:
						logging.error("Rssi concersion error %s", e)
						print "Conversion error!"
						continue

					if rssi_avg is not None:
						logging.debug("average rssi: %s", rssi_avg)
						position = check_proximity(rssi_avg)
						logging.debug("position is %s", position)
						print "position:", position, "---", rssi_avg

						#sistemare un pochino
						if position < 4:
							if not print_dir:
								print "ARROW", direction
								print_dir = True
								logging.info("Printing out direction: ARROW %s", direction)
						
						if position < 2:
							if not arrived:
								arrived = True
								logging.info("The user is arrived to destination")
					
						if position > 3:
							if print_dir:
								print_dir = False
								logging.info("Turn off the projector")
								logging.debug("Projector is off because position is %s and avg_rssi is %s", position, rssi_avg)
								print "turn off the projector"

					 

			

	def stop(self):
		self.is_running = False


def signal_handler(signal, frame):
	logging.info("Signal Handler arrived")
	print "Exit!"

	#close all the thread in thread list
	logging.debug("the thread are: %s", t_sniffer)
	for user in t_sniffer:
		logging.debug("closing thread %s", user)
		user.stop()

	logging.info("stopping all ping thread")
	t_mqtt.stop()
	logging.info("Stopping mqtt thread")
	try:
		killall_ping = subprocess.check_output(['killall', 'l2ping'], stderr=subprocess.PIPE)
		logging.debug("Closing l2ping process %s", killall_ping)
	except subprocess.CalledProcessError as e:
		logging.warning(e)
		logging.warning("No l2ping process")

	

	logging.info("Closing the program")
	sys.exit(0)

def args_parser():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hrv', ['help', 'rasp=', 'verbose='])
		logging.debug("Input params %s", opts)
	except getopt.GetoptError as err:
		print str(err)
		#logging.warning("params error"+opts)
		#usage()
		print "Error, TODO how to use"
		logging.warning("exit program")
		sys.exit(2)

	global rasp
	rasp = 0
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			logging.debug("help")
			print "TODO how to use"
			#usage()
			logging.info("exit program")
			sys.exit(2)
		elif opt in ('-r', '--rasp'):
			rasp = 1
			logging.debug("rasp mode enabled %d", rasp)
		elif opt in ('-v', '--verbose'):
			logging.getLogger().setLevel(logging.DEBUG)
			logging.debug("vervose mode enabled %s", opt)
		else:
			#usage()
			logging.warning("some error in params ",params)
			print "Exit.. TODO how to use"
			logging.info("exit program")
			sys.exit(2)

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

#### MAIN ####
if __name__ == "__main__":
	logging.info("_____________________________")
	logging.info("SM4RT_D1R3CT10Nz v0.3 thread")
	signal.signal(signal.SIGINT, signal_handler)
	print "SM4RT_D1R3CT10Nz v0.3 thread", rasp_id
	logging.info("Starting main...")

	args_parser()

	if rasp:
		broker_address = broker_address_cluster
		logging.debug("Set broker address in rasp mode: "+ broker_address)

	logging.info("the broker_address is "+broker_address)

	t_mqtt = MqttHandler.MqttThread(broker_address, topic_name)
	t_mqtt.setDaemon(True)
	logging.info("Setting up the mqtt thread")
	
	global t_sniffer
	t_sniffer = []

	t_mqtt.start()
	

	while True:
		if not MqttHandler.q.empty():
			item = MqttHandler.q.get()
			logging.info("A new message is arrived. ID %s" ,item['id'])
			logging.info(item)
			print "new message is arrived... ID is:", item['id']
			user = PingThread(item)
			t_sniffer.append(user)

			logging.debug("Creating a new thread")
			user.start()
