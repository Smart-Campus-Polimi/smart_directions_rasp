#!/usr/bin/python

import logging
import threading
import json
import Queue
import paho.mqtt.client as mqtt
from collections import namedtuple

import thread_test

BUF_SIZE = 10
q = Queue.Queue(BUF_SIZE)	

StartMsg = namedtuple('StartMsg', ['mac_address', 'place_id', 'id', 'timestamp'])
StopMsg = namedtuple('StopMsg', ['mac_address', 'timestamp'])

class Receiver:
	def __init__(self, queue_sub):
		self.queue_sub = queue_sub
	def on_connect(self, client, userdata, flags, rc):
			#print "Connected with result code "+str(rc)
			logging.debug("MQTT: connected with result code "+str(rc))
			# Subscribing in on_connect() means that if we lose the connection and
			# reconnect then subscribeptions will be renewed.
			client.subscribe(thread_test.topic_name)
			client.subscribe("stop_ping")
			logging.debug("Subscribing to %s", thread_test.topic_name)

	def on_message(self, client, userdata, msg):
			#print msg.topic+" "+str(msg.payload)
			logging.debug("Receiving a msg with payload %s", str(msg.payload.decode("utf-8")))
			msg_mqtt_raw = str(msg.payload.decode("utf-8"))
			
			#can be deleted
			if (msg.payload=="disconnect"):
				logging.debug("disconnection through message")
				client.disconnect()
				return 

			if msg.topic == thread_test.topic_name:
				msg_mqtt_raw = "[" + msg_mqtt_raw + "]"
			
				try:
					msg_mqtt = json.loads(msg_mqtt_raw)
					logging.debug("json converted. Content: %s", msg_mqtt)
				except ValueError, e:
					logging.error("Malformed json %s. Json: %s", e, msg_mqtt_raw)
					msg_mqtt = msg_mqtt_raw[:-1]
					msg_mqtt = msg_mqtt[1:]

				start_msg = StartMsg(id=msg_mqtt[0]['id'],
						 mac_address=msg_mqtt[0]['mac_address'],
						 place_id=msg_mqtt[0]['place_id'],
						 timestamp=msg_mqtt[0]['timestamp'])

				#add message to queue
				if not self.queue_sub.full():
					self.queue_sub.put(start_msg)
					logging.debug("putting msg %s in queue", start_msg)
				else:
					logging.warning("Queue is full %s", q)
					print "Queue is full!"

			
			elif msg.topic == "stop_ping":
				stop_msg = StopMsg(mac_address=msg_mqtt_raw, timestamp="10:21:21")
				self.queue_sub.put(stop_msg)


	def on_disconnect(self, client, userdata, rc):
		if rc != 0:
			logging.error("Unexpected disconnection %d", rc)
			print("Unexpected disconnection.")
		else:
			logging.debug("disconnection ok")

class MqttThread(threading.Thread):
	def __init__(self, queue_sub, queue_pub, host):
		threading.Thread.__init__(self)
		self.queue_sub = queue_sub
		self.queue_pub = queue_pub
		self.client = mqtt.Client()
		self.host = host

	def run(self):
		print "creating client --- host: ", self.host
		logging.info("Mqtt thread runs")
		receiver = Receiver(self.queue_sub)
		self.client.loop_start()
		logging.info("Mqtt starts loop")
		self.client.on_connect = receiver.on_connect
		self.client.on_message = receiver.on_message

		self.client.connect_async(self.host, 1883)
		logging.info("opening mqtt connection")

		while True:
			if not self.queue_pub.empty():
				final_pos_msg = self.queue_pub.get()
				print "receiving a message from the main. the mac address ", final_pos_msg, " is arrived to the final destination"
				
				self.client.publish("stop_ping", final_pos_msg)
				
		#loop until disconnect
		#client.loop_forever()
			
	
	def stop(self):
		self.client.disconnect()
		logging.info("disconnect mqtt")