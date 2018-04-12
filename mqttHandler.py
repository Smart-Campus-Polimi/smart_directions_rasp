#!/usr/bin/python

import subprocess
import json

class mqttHandler:

	def __init__(self):
		pass

	def start(self, broker, topic):
		self.broker = broker
		self.topic = topic

		print "mqtt starts on", self.broker, "topic ", self.topic
		self.mqtt = subprocess.Popen(['mosquitto_sub', '-t', self.topic, '-h', self.broker], bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		return self.mqtt

	def check_msg(self):

		if not self.mqtt:
			self.start()


		line = self.mqtt.stdout.readline()

		if line:

			msg_mqtt_raw = "[" + line + "]"
			msg_mqtt = json.loads(msg_mqtt_raw)
	
			return msg_mqtt