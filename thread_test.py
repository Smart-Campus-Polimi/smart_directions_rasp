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
		logging.debug("Mqtt thread runs")
		receiver = Receiver()
		self.client.loop_start()
		logging.debug("Mqtt starts loop")
		self.client.on_connect = receiver.on_connect
		self.client.on_message = receiver.on_message

		self.client.connect_async(self.host, 1883)
		logging.debug("opening mqtt connection")
		#loop until disconnect
		#client.loop_forever()
			
	
	def stop(self):
		self.client.disconnect()
		logging.warning("disconnect mqtt")

######	

class PingThread(threading.Thread):
	def __init__(self, user):
		threading.Thread.__init__(self)
		self.user = user

	def run(self):
		mac_target = self.user['mac_address']
		place_id_target = self.user['place_id']
		timestamp_target = self.user['timestamp']

		tree = ET.parse('map.xml')
		root = tree.getroot()

		direction, final = xml_parser.find_direction(root, place_id_target, rasp_id)
		
		print "direction: ", direction
		print "final?", final
		print "Hi, i'm ", mac_target, " mac address"
		print "starting ping ... "

		bt = bluetoothHandler.bluetoothHandler()
		bt.start(mac_target)
		self.is_running = True

		sum_rssi = 0 
		count = 0
		rssi_avg = 0
		arrived = False
		oor_count = 0

		while self.is_running:
			rssi = bt.rssi()
			
			if rssi is not None:
				if rssi == "OOR":
					print "Out of Range"
					if arrived:
						oor_count += 1
						if oor_count > 3:
							print "users pass the destination"
							if final:
								print "stop all the ping"
				else:
					try:
						rssi = float(rssi)
					except ValueError:
						print "Conversion error!"
						break	

					rssi_avg, count, sum_rssi = average_rssi(rssi, count, sum_rssi)
					if rssi_avg is not None:
						position = check_proximity(rssi_avg)
						if (position == "very near") or (position == "very near"):
							arrived = True
						print position, "---", rssi_avg
					
					 

			

	def stop(self):
		self.is_running = False


def signal_handler(signal, frame):
	logging.debug("Signal Handler arrived")
	print "Exit!"

	#close all the thread in thread list
	logging.debug("the thread are: %s", t_sniffer)
	for user in t_sniffer:
		logging.debug("closing thread ")
		logging.debug(user)
		user.stop()

	logging.debug("stopping all ping thread")
	t_mqtt.stop()
	logging.debug("Stopping mqtt thread")
	try:
		killall_ping = subprocess.check_output(['killall', 'l2ping'], stderr=subprocess.PIPE)
		logging.debug("Closing l2ping process %s", killall_ping)
	except subprocess.CalledProcessError as e:
		logging.warning(e)
		logging.warning("No l2ping process")

	

	logging.debug("Closing the program")
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
			logging.debug("exit program")
			sys.exit(2)
		elif opt in ('-r', '--rasp'):
			rasp = 1
			logging.debug("rasp mode enabled %d", rasp)
		else:
			#usage()
			logging.warning("some error in params ",params)
			print "Exit.. TODO how to use"
			logging.debug("exit program")
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
		return "very very near"
	if rssi > -1.0 and rssi <=0.5:
		return "very near"
	if rssi > -10 and rssi <=-1.0:
		return "near"
	if rssi > -20 and rssi <=-10:
		return "visible"
	if rssi <= -20:
		return "in range"

#### MAIN ####
if __name__ == "__main__":
	logging.debug("_____________________________")
	signal.signal(signal.SIGINT, signal_handler)
	print "SM4RT_D1R3CT10Nz v0.3 thread", rasp_id
	logging.debug("Starting main...")

	args_parser()

	if rasp:
		broker_address = broker_address_cluster
		logging.debug("Set broker address in rasp mode: "+ broker_address)

	logging.debug("the broker_address is "+broker_address)

	t_mqtt = MqttThread(broker_address)
	t_mqtt.setDaemon(True)
	logging.debug("Setting up the mqtt thread")
	
	global t_sniffer
	t_sniffer = []

	t_mqtt.start()
	

	while True:
		if not q.empty():
			item = q.get()
			logging.debug("A new message is arrived. ID %s" ,item['id'])
			logging.info(item)
			print "new message is arrived... ID is:", item['id']
			user = PingThread(item)
			t_sniffer.append(user)

			logging.debug("Creating a new thread")
			user.start()
