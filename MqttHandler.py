#!/usr/bin/python

import threading
import json
import Queue
import paho.mqtt.client as mqtt
from collections import namedtuple

import constants as c



StartMsg = namedtuple('StartMsg', ['mac_address', 'place_id', 'id', 'timestamp', 'color'])
StopMsg = namedtuple('StopMsg', ['mac_address', 'timestamp'])

class Receiver:
	def __init__(self, queue_sub):
		self.queue_sub = queue_sub


	def _subscribe_to_topic(self, my_topics, client):
			for topic in my_topics:
				client.subscribe(topic, qos=1)
				c.logging.debug("Subscribing to %s", topic)
	def _receive_startMsg(self, msg):
		c.logging.info("starting msg is received")
		msg = "[" + msg + "]"
	
		try:
			msg_mqtt = json.loads(msg)
			c.logging.debug("json converted. Content: %s", msg_mqtt)
		except ValueError, e:
			c.logging.error("Malformed json %s. Json: %s", e, msg)
			msg_mqtt = msg[:-1]
			msg_mqtt = msg_mqtt[1:]

		start_msg = StartMsg(id=msg_mqtt[0]['id'],
				 			 mac_address=msg_mqtt[0]['mac_address'],
				 			 place_id=msg_mqtt[0]['place_id'],
				 			 timestamp=msg_mqtt[0]['timestamp'], 
							 color=msg_mqtt[0]['color'])

		#add message to queue
		if not self.queue_sub.full():
			self.queue_sub.put(start_msg)
			c.logging.debug("putting msg %s in queue", start_msg)
		else:
			c.logging.warning("Queue is full %s", q)

	def _receive_stopMsg(self, msg):
		c.logging.info("Stopping msg is received")
		stop_msg = StopMsg(mac_address=msg, timestamp="10:21:21") #update the timestamp
		c.logging.info("Putting the msg in the sub queue")
		self.queue_sub.put(stop_msg)

	def on_connect(self, client, userdata, flags, rc):
			c.logging.debug("MQTT: connected with result code "+str(rc))
			
			self._subscribe_to_topic(c.TOPIC_LIST, client)

	def on_message(self, client, userdata, msg):
			c.logging.info("Receiving a msg with payload %s", str(msg.payload.decode("utf-8")))
			msg_mqtt_raw = str(msg.payload.decode("utf-8"))
			print "receive a msg in MQTT"
			
			if msg.topic == c.TOPIC_LIST[0]:
				self._receive_startMsg(msg_mqtt_raw)
			
			elif msg.topic == c.TOPIC_LIST[1]:
				self._receive_stopMsg(msg_mqtt_raw)

	def on_disconnect(self, client, userdata, rc):
		if rc != 0:
			c.logging.error("Unexpected disconnection %d", rc)
			print("Unexpected disconnection.")
		else:
			c.logging.debug("disconnection ok")

class MqttThread(threading.Thread):
	def __init__(self, queue_sub, queue_pub, host):
		threading.Thread.__init__(self)
		self.queue_sub = queue_sub
		self.queue_pub = queue_pub
		self.client = mqtt.Client()
		self.host = host

	def run(self):
		print "Creating client ---> Host: ", self.host
		c.logging.info("Mqtt thread runs")
		receiver = Receiver(self.queue_sub)
		self.client.loop_start()
		c.logging.info("Mqtt starts loop")
		self.client.on_connect = receiver.on_connect
		self.client.on_message = receiver.on_message

		self.client.connect_async(self.host, 1883)
		c.logging.info("Opening mqtt connection")

		while True:
			if not self.queue_pub.empty():
				#the while task is to wait that an user is arrived to the final sniffer and to publish a msg
				final_pos_msg = self.queue_pub.get()
				c.logging.info("%s is arrived to the final destination", final_pos_msg)
				
				self.client.publish(c.TOPIC_LIST[1], final_pos_msg, qos=1)
				c.logging.info("Sending the final message")

	
	def stop(self):
		c.logging.info("disconnect mqtt")
		self.client.disconnect()
		
