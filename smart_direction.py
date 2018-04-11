#!/usr/bin/python

import os
import sys
import subprocess
import threading
import json
import pprint as pp
import paho.mqtt.client as mqtt
from time import sleep




broker_address = "192.168.1.74" 
topic_name = "topic/rasp4/directions"

def on_message(client, userdata, message):
	global users_list
	msg_mqtt_raw = "[" + str(message.payload.decode("utf-8")) + "]"
	msg_mqtt = json.loads(msg_mqtt_raw)


	users_list[msg_mqtt[0]["id"]] = msg_mqtt[0]["content"]

	print "message topic= ",message.topic 
	#print "message qos=",message.qos
	#print "message retain flag=",message.retain

 
#### MQTT Thread ####
class mqttThread(threading.Thread):
	def __init__(self,name):
		threading.Thread.__init__(self)
		self.name = name



	def run(self):
		print "creating new mqtt instance"
		client = mqtt.Client("P1")
		print "connecting to broker on host ", broker_address
		client.connect(broker_address)
		client.on_message = on_message #attach function to callback

		print "Subscribing to topic "+topic_name
		client.subscribe(topic_name)

		client.loop_forever()

#### END MQTT Thread ####



#### MAIN ####
if __name__ == "__main__":
	print "SM4RT_D1R3CT10Nz v0.1"

	users_list = {}
	users_number = len(users_list)
	thread_mqtt = mqttThread("mqtt")

	thread_mqtt.start()

	while 1:
		if(len(users_list) != users_number):
			pp.pprint(users_list)
			users_number = len(users_list)

#### END MAIN ####