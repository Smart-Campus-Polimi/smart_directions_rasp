#!/usr/bin/python

import logging
import threading
import json
import Queue
import paho.mqtt.client as mqtt

BUF_SIZE = 10
q = Queue.Queue(BUF_SIZE)	

class Receiver:
	def __init__(self, topic):
		self.topic = topic
	def on_connect(self, client, userdata, flags, rc):
			#print "Connected with result code "+str(rc)
			logging.debug("MQTT: connected with result code "+str(rc))
			# Subscribing in on_connect() means that if we lose the connection and
			# reconnect then subscribeptions will be renewed.
			client.subscribe(self.topic)
			logging.debug("Subscribing to %s", self.topic)

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
	def __init__(self, host, topic):
		threading.Thread.__init__(self)
		self.client = mqtt.Client()
		self.host = host
		self.topic = topic

	def run(self):
		print "creating client --- host: ", self.host
		logging.info("Mqtt thread runs")
		receiver = Receiver(self.topic)
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