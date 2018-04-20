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
import pprint as pp
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
			user = PingHandler.PingThread(item)
			t_sniffer.append(user)

			logging.debug("Creating a new thread")
			user.start()
