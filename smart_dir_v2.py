#!/usr/bin/python

import os
import sys
import subprocess
import threading
import json
import signal
import bluetoothHandler
import mqttHandler
import pprint as pp
from time import sleep

broker_address = "192.168.1.74"
#broker_address = "10.0.2.15" 
topic_name = "topic/rasp4/directions"


class mqttThread(threading.Thread):
	def __init__(self, broker, topic):
		threading.Thread.__init__(self)
		self.broker = broker
		self.topic = topic

	def run(self):
		print "creating new mqtt instance"
		mqtt = mqttHandler.mqttHandler()
		mqtt.start(self.broker, self.topic)
		
		self.is_running = True
		while self.is_running:
			mqtt_msg = mqtt.check_msg()
			
			global active_users
			active_users[mqtt_msg[0]["id"]] = mqtt_msg[0]["content"]

	def stop(self):
		self.is_running = False



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
		count_out = 0
		
		self.is_running = True
		while self.is_running:
			rssi_raw = bt.rssi()
			if rssi_raw != None:
				#print int(rssi_raw), sum_rssi
				sum_rssi = sum_rssi + int(rssi_raw)
				count += 1
				if count == 20:
					rssi_avg = float(float(sum_rssi)/count)
					if rssi_avg>=-0.2 and rssi_avg <= 0.5:
						print "very near",rssi_avg
					elif rssi_avg <= -20:
						print "distant",rssi_avg
					elif rssi_avg > -20.0 and rssi_avg <=-5.0:
						print "quite distant",rssi_avg
					elif rssi_avg > -5.0 and rssi_avg <-0.2:
						print "near",rssi_avg
					elif rssi_avg > 0.5:
						print "appiccicato",rssi_avg
					
					sum_rssi = 0 
					count = 0

			else:
				count_out += 1
				if count_out==20:
					print "out of range"
					count_out = 0


	def stop(self):
		self.is_running = False


def signal_handler(signal, frame):
	print "Exit Program..."
	thread_mqtt.stop()
	for th in thread_user:
		th.stop()
	running = 0
	sys.exit(0)


#new users actions
def new_user_found(user):
	print "new user", user
	
	ping_device = pingThread(user)
	ping_device.start()

	return ping_device

#### MAIN ####
if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	print "SM4RT_D1R3CT10Nz v0.2"

	running = 1
	active_users = {}
	thread_mqtt = mqttThread(broker_address, topic_name)
	thread_mqtt.start()
	users_list = []
	users_number = len(users_list)
	thread_user = []
	
	while running:
		#new user appear in dictionary
		if(len(active_users) != users_number):
			#if is the first one
			if len(users_list) == 0:
				#retrieve the first key in dictionary
				users_list.append(active_users.keys()[0])
				thread_user.append(new_user_found(active_users[active_users.keys()[0]]))

			else:
				#check which users is the new one
				for usr in active_users.keys():
					if usr not in users_list:
						users_list.append(usr)
						thread_user.append(new_user_found(active_users[usr]))

						
			
			users_number = len(active_users)

	thread_mqtt.join()
	#sleep(200)