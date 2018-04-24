#!/usr/bin/python

import threading
import signal
import time
import sys
import json
import getopt
import Queue
import subprocess
import logging
import xml.etree.ElementTree as ET
import pprint as pp
#my imports
import MqttHandler
import PingHandler


pwd = subprocess.check_output(['pwd']).rstrip() + "/"
rasp_id = subprocess.check_output(['cat', pwd+'config/raspi-number.txt'])[:1]
logging.basicConfig(filename= 'rasp'+rasp_id+'.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug("Start smart directions on rasp "+rasp_id)
logging.debug("directory: "+ pwd)

broker_address = "10.0.2.15" 
broker_address_cluster = "192.168.1.74"
topic_name = "topic/rasp4/directions"
proj_status = False


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


def display_image(my_direction):
	arrow_path = "arrows/Green_arrow_"+my_direction+".png"
	print arrow_path
	subprocess.Popen(['killall', 'fbi'])
	subprocess.Popen(['tvservice', '-p'])
	subprocess.Popen(['fbi','-a', '--noverbose', '-T', '1', arrow_path])

def turn_off_screen():
	subprocess.Popen(['killall', 'fbi'])
	subprocess.Popen(['tvservice', '-o'])

#### MAIN ####
if __name__ == "__main__":
	logging.info("_____________________________")
	logging.info("SM4RT_D1R3CT10Nz v0.3 thread")
	signal.signal(signal.SIGINT, signal_handler)
	print "SM4RT_D1R3CT10Nz v0.3 thread", rasp_id
	logging.info("Starting main...")
	logo_path = 'arrows/smart_dir_logo.png'
	subprocess.Popen(['fbi','-a', '--noverbose', '-T', '1', logo_path])
	args_parser()

	if rasp:
		broker_address = broker_address_cluster
		logging.debug("Set broker address in rasp mode: "+ broker_address)

	#opening map
	logging.info("Opening map")
	tree = ET.parse('map.xml')
	map_root = tree.getroot()

	logging.info("the broker_address is "+broker_address)

	mqtt_sub_q = Queue.Queue()
	mqtt_pub_q = Queue.Queue()


	t_mqtt = MqttHandler.MqttThread(mqtt_sub_q, mqtt_pub_q, broker_address)
	t_mqtt.setDaemon(True)
	logging.info("Setting up the mqtt thread")
	
	global t_sniffer
	t_sniffer = []

	t_mqtt.start()
	
	sniffer_queue = Queue.Queue()
	stop_queue = Queue.Queue()

	while True:
		if not mqtt_sub_q.empty():
			item = mqtt_sub_q.get()
			logging.info("A new message is arrived. %s", item)
			logging.info(item)
			print "new message is arrived... ID is:", item

			if type(item).__name__ == "StartMsg":
				print "START MSG"
				user = PingHandler.PingThread(item, map_root, sniffer_queue, stop_queue)
				t_sniffer.append(user)

				logging.debug("Creating a new thread")
				user.start()

			elif type(item).__name__ == "StopMsg":
				print "STOP MESSAGE"
				mac_target, timestamp = item
				print "stop msg istem: ", item
				stop_queue.put(item)
				

		if not sniffer_queue.empty():
			proj_msg = sniffer_queue.get()
			logging.info("A projector msg is arrived")
			logging.debug("Reading proj queue msg: %s", proj_msg)

			if type(proj_msg).__name__ == "ProjMsg":
				mac_target, direction, new_proj_status, final_pos, timestamp = proj_msg
				if not proj_status:
					if new_proj_status:
						logging.info("Turn ON the projector")
						print "turn on the proj ", direction
						display_image(direction)
						proj_status = new_proj_status
				elif proj_status:
					if not new_proj_status:
						logging.info("Turn OFF the projector")
						print "turn off the proj"
						proj_status = new_proj_status
						turn_off_screen()

				if final_pos:
					print "user is arrived to the final step, sending msg to the other sniffers"
					mqtt_pub_q.put(mac_target)
					proj_status = False
			
			#elif type(proj_msg).__name__ == "StopMsg":
			#	print "qua"
			#	sniffer_queue.put(proj_msg)

