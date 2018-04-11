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
	global users
	msg_mqtt_raw = "[" + str(message.payload.decode("utf-8")) + "]"
	msg_mqtt = json.loads(msg_mqtt_raw)


	users[msg_mqtt[0]["id"]] = msg_mqtt[0]["content"]

	#print "message topic= ",message.topic 
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

#### PING Thread ####
class pingThread(threading.Thread):
	def __init__(self, user):
		threading.Thread.__init__(self)
		self.user = user

	def run(self):
		print "new thread with device ", user["mac_address"]


#### END PING Thread ####

#new users actions
def new_user_found(user):
	print "new user"
	pp.pprint(user)
	#ping_device = pingThread(user)
	#ping_device.start()

#### MAIN ####
if __name__ == "__main__":
	print "SM4RT_D1R3CT10Nz v0.1"

	users = {}
	users_list = []
	users_number = len(users_list)
	thread_mqtt = mqttThread("mqtt")

	thread_mqtt.start()

	while True:
		#new user appear in dictionary
		if(len(users) != users_number):
			#if is the first one
			if len(users_list) == 0:
				#retrieve the first key in dictionary
				users_list.append(users.keys()[0])
				new_user_found(users[users.keys()[0]])

			else:
				#check which users is the new one
				for usr in users.keys():
					if usr not in users_list:
						users_list.append(usr)
						new_user_found(users[usr])

			print "\n\n"

			
			
			users_number = len(users)

#### END MAIN ####