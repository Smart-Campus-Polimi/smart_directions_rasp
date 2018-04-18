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
import paho.mqtt.client as mqtt

BUF_SIZE = 10
AVG_RATE = 20
q = Queue.Queue(BUF_SIZE)


pwd = subprocess.check_output(['pwd']).rstrip() + "/"
rasp_id = subprocess.check_output(['cat', pwd+'config/raspi-number.txt'])[:1]
logging.basicConfig(filename= 'raspa.log',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug("Start smart directions on rasp "+rasp_id)
logging.debug("directory: "+ pwd)

broker_address = "10.0.2.15" 
broker_address_cluster = "192.168.1.74"
topic_name = "topic/rasp4/directions"


global client
class Receiver:
	def on_connect(self, client, userdata, flags, rc):
			print "Connected with result code "+str(rc)
			logging.debug("Connected with result code "+str(rc))
			# Subscribing in on_connect() means that if we lose the connection and
			# reconnect then subscribeptions will be renewed.
			client.subscribe(topic_name)
			logging.debug("Subscribing to %s", topic_name)

	def on_message(self, client, userdata, msg):
			#print msg.topic+" "+str(msg.payload)
			logging.debug("Receiving a msg with payload %s", str(msg.payload.decode("utf-8")))
			msg_mqtt_raw = "[" + str(msg.payload.decode("utf-8")) + "]"
			
			if (msg.payload=="disconnect"):
				logging.debug("disconnection through message")
				client.disconnect()
				return 


			try:
				msg_mqtt = json.loads(msg_mqtt_raw)
				logging.debug("json concerted. Content: %s", msg_mqtt)
			except ValueError, e:
				logging.error("Malformed json %s", e)
				msg_mqtt = msg_mqtt_raw[:-1]
				msg_mqtt = msg_mqtt[1:]

			#add message to queue
			if not q.full():
				q.put(msg_mqtt[0])
				logging.debug("putting msg %s in queue", msg_mqtt[0])
			else:
				logging.warning("Queue is full %s", q)
				print "Queue is full!"


	def on_disconnect(self, client, userdata, rc):
		if rc != 0:
			logging.error("Unexpected disconnection %d", rc)
			print("Unexpected disconnection.")
		else:
			logging.debug("disconnection ok")

class MqttThread(threading.Thread):
	def __init__(self, host):
		threading.Thread.__init__(self)
		self.client = mqtt.Client()
		self.host = host

	def run(self):
		print "creating client --- host: ", self.host
		logging.info("Mqtt thread runs")
		receiver = Receiver()
		self.client.loop_start()
		logging.info("Mqtt starts loop")
		self.client.on_connect = receiver.on_connect
		self.client.on_message = receiver.on_message

		self.client.connect_async(self.host, 1883)
		logging.info("opening mqtt connection")
		#loop until disconnect
		#client.loop_forever()
			
	
	def stop(self):
		self.client.disconnect()
		logging.info("disconnect mqtt")

######	

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
			logging.debug("inside while loop")
			rssi = bt.rssi()
			logging.debug("reading rssi %s", rssi)


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
						#logging.debug("puntual rssi: %s", rssi)
					except ValueError as e:
						logging.error("Rssi concersion error %s", e)
						print "Conversion error!"
						break	

					rssi_avg, count, sum_rssi = average_rssi(rssi, count, sum_rssi)
					if rssi_avg is not None:
						logging.debug("average rssi: %s", rssi)
						position = check_proximity(rssi_avg)
						if position < 4:
							if not print_dir:
								print "ARROW", direction
								print_dir = True
							logging.info("Printing out direction")
						logging.debug("position is %s", position)
						if position < 2:
							arrived = True
							logging.info("The user is arrived to destination")
						print "position:", position, "---", rssi_avg
					
					 

			

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
		opts, args = getopt.getopt(sys.argv[1:], 'h:r', ['help', 'rasp='])
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
		logging.debug(position)
		return 0
	elif rssi > -1.0 and rssi <=0.5:
		position = "very near"
		logging.debug(position)
		return 1
	elif rssi > -10 and rssi <=-1.0:
		position = "near"
		logging.debug(position)
		return 2
	elif rssi > -20 and rssi <=-10:
		position = "visible"
		logging.debug(position)
		return 3
	elif rssi <= -20:
		position = "in range"
		logging.debug(position)
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

	t_mqtt = MqttThread(broker_address)
	t_mqtt.setDaemon(True)
	logging.info("Setting up the mqtt thread")
	
	global t_sniffer
	t_sniffer = []

	t_mqtt.start()
	

	while True:
		if not q.empty():
			item = q.get()
			logging.info("A new message is arrived. ID %s" ,item['id'])
			logging.info(item)
			print "new message is arrived... ID is:", item['id']
			user = PingThread(item)
			t_sniffer.append(user)

			logging.debug("Creating a new thread")
			user.start()
