#!/usr/bin/python

import os
import sys
import signal
import subprocess
import threading
import json
import bluetoothHandler
import subprocess
import pprint as pp
import paho.mqtt.client as mqtt
from time import sleep




#broker_address = "192.168.1.74"
broker_address = "10.0.2.15" 
topic_name = "topic/rasp4/directions"

def on_message(client, userdata, message):
	#global users
	msg_mqtt_raw = "[" + str(message.payload.decode("utf-8")) + "]"
	msg_mqtt = json.loads(msg_mqtt_raw)
	global users
	users[msg_mqtt[0]["id"]] = msg_mqtt[0]["content"]
	print "lol"
	new_user_found(msg_mqtt[0]["content"])
	
 
#### MQTT Thread ####
class mqttThread(threading.Thread):
	def __init__(self,name):
		threading.Thread.__init__(self)
		self.name = name



	def run(self):
		print "creating new mqtt instance"
		global client
		client = mqtt.Client("P1")
		print "connecting to broker on host ", broker_address
		client.connect(broker_address)
		
		client.on_message = on_message #attach function to callback
		print "Subscribing to topic "+topic_name
		client.subscribe(topic_name)
		client.loop_forever()


		

#### END MQTT Thread ####

#### PING Thread ####
class pingThread(threading.Thread):
	def __init__(self, user):
		threading.Thread.__init__(self)
		self.user = user

	def run(self):
		print "new thread for the device with mac address", self.user["mac_address"]
		bt = bluetoothHandler.bluetoothHandler()
		bt.start(self.user["mac_address"])
		
		sum_rssi = 0
		count = 0
		
		while True:
			rssi_raw = bt.rssi()
			if rssi_raw != None:
				#print int(rssi_raw), sum_rssi
				sum_rssi = sum_rssi + int(rssi_raw)
				count += 1
				if count == 20:
					rssi_avg = float(float(sum_rssi)/count)
					if rssi_avg>=-0.2 and rssi_avg <= 0.5:
						print "very near"
					elif rssi_avg <= -20:
						print "distant"
					elif rssi_avg > -20.0 and rssi_avg <=-5.0:
						print "quite distant"
					elif rssi_avg > -5.0 and rssi_avg <-0.2:
						print "near"
					elif rssi_avg > 0.5:
						print "appiccicato"
					print rssi_avg
					sum_rssi = 0 
					count = 0

			else:
				print "out of range"



#### END PING Thread ####

#new users actions
def new_user_found(user):
	print "new user", user

	ping_device = pingThread(user)
	ping_device.start()

def signal_handler(signal, frame):
	print "esci"
	global client
	client.disconnect()
	thread_mqtt.join()
	sys.exit(0)

#### MAIN ####
if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	print "SM4RT_D1R3CT10Nz v0.1"

	users = {}
	users_list = []
	users_number = len(users_list)

	thread_mqtt = mqttThread("mqtt")
	#thread_mqtt.setDaemon(True)


	thread_mqtt.start()


	sleep(1000000)
	
	

'''
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
			
			users_number = len(users)
'''

#### END MAIN ####