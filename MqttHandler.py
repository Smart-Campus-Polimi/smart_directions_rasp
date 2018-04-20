#!/usr/bin/python

import logging
import threading
import json
import Queue
import paho.mqtt.client as mqtt

import thread_test

BUF_SIZE = 10
q = Queue.Queue(BUF_SIZE)	

class Receiver:
	def __init__(self, queue_sub):
		self.queue_sub = queue_sub
	def on_connect(self, client, userdata, flags, rc):
			#print "Connected with result code "+str(rc)
			logging.debug("MQTT: connected with result code "+str(rc))
			# Subscribing in on_connect() means that if we lose the connection and
			# reconnect then subscribeptions will be renewed.
			client.subscribe(thread_test.topic_name)
			logging.debug("Subscribing to %s", thread_test.topic_name)

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
				logging.error("Malformed json %s. Json: %s", e, msg_mqtt_raw)
				msg_mqtt = msg_mqtt_raw[:-1]
				msg_mqtt = msg_mqtt[1:]

			#add message to queue
			if not self.queue_sub.full():
				self.queue_sub.put(msg_mqtt[0])
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
				sniffer_msg = self.queue_pub.get()
				print "in mqtt thread ", sniffer_msg
		#loop until disconnect
		#client.loop_forever()
			
	
	def stop(self):
		self.client.disconnect()
		logging.info("disconnect mqtt")