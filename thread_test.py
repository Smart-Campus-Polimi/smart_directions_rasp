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
import pprint as pp
import paho.mqtt.client as mqtt

BUF_SIZE = 10
q = Queue.Queue(BUF_SIZE)

broker_address = "10.0.2.15" 
broker_address_cluster = "192.168.1.74"
topic_name = "topic/rasp4/directions"

global client
class Receiver:
	def on_connect(self, client, userdata, flags, rc):
			print "Connected with result code "+str(rc)
			# Subscribing in on_connect() means that if we lose the connection and
			# reconnect then subscribeptions will be renewed.
			client.subscribe(topic_name)

	def on_message(self, client, userdata, msg):
			#print msg.topic+" "+str(msg.payload)
			msg_mqtt_raw = "[" + str(msg.payload.decode("utf-8")) + "]"
			
			if (msg.payload=="disconnect"):
				client.disconnect()
				return 


			try:
				msg_mqtt = json.loads(msg_mqtt_raw)
			except ValueError, e:
				msg_mqtt = msg_mqtt_raw[:-1]
				msg_mqtt = msg_mqtt[1:]

			#add message to queue
			if not q.full():
				q.put(msg_mqtt)
			else:
				print "Queue is full!"


	def on_disconnect(self, client, userdata, rc):
		if rc != 0:
			print("Unexpected disconnection.")

class MqttThread(threading.Thread):
	def __init__(self, host):
		threading.Thread.__init__(self)
		self.client = mqtt.Client()
		self.host = host

	def run(self):
		print "creating client --- host: ", self.host
		receiver = Receiver()
		self.client.loop_start()
		self.client.on_connect = receiver.on_connect
		self.client.on_message = receiver.on_message

		self.client.connect_async(self.host, 1883)
		#loop until disconnect
		#client.loop_forever()
			
	
	def stop(self):
		self.client.disconnect()

######

class PingThread(threading.Thread):
	def __init__(self, user):
		threading.Thread.__init__(self)
		self.user = user

	def run(self):
		print "ciao, sono il thread di ", self.user
		print "parto a pingare... "
		bt = bluetoothHandler.bluetoothHandler()
		bt.start(self.user)
		self.is_running = True
		while self.is_running:
			bt.rssi()

	def stop(self):
		self.is_running = False

def signal_handler(signal, frame):
	print "esci"
	user.stop()
	t_mqtt.stop()
	subprocess.Popen(['killall', 'l2ping'])
	sys.exit(0)


def args_parser():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'h:r', ['help', 'rasp='])
	except getopt.GetoptError as err:
		print str(err)
		#usage()
		print "Error, TODO how to use"
		sys.exit(2)

	global rasp
	rasp = 0
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			print "TODO how to use"
			#usage()
			sys.exit(2)
		elif opt in ('-r', '--rasp'):
			rasp = 1
		else:
			#usage()
			print "Exit.. TODO how to use"
			sys.exit(2)

#### MAIN ####
if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	print "SM4RT_D1R3CT10Nz v0.3 thread"
	args_parser()

	if rasp:
		broker_address = broker_address_cluster


	t_mqtt = MqttThread(broker_address)
	t_mqtt.setDaemon(True)

	t_sniffer = []

	t_mqtt.start()
	

	while True:
		if not q.empty():
			item = q.get()
			print "new message is arrived... mac address is: ", item
			user = PingThread(item)
			t_sniffer.append(user)
			user.start()
