#!/usr/bin/python

import threading
import signal
import time
import sys
import json
import getopt
import Queue
import subprocess
import logging
import os
import xml.etree.ElementTree as ET
import pprint as pp
from collections import namedtuple
from datetime import datetime
from time import strftime, localtime
#my imports
import MqttHandler
import PingHandler
import ProjectorHandler


##### GLOBAL VARS ####
global t_sniffer
t_sniffer = []
global timer_sniffer
timer_sniffer = []
global stop_list
stop_list = []
global proj_status
proj_status = False
global close_proj
close_proj = True
global fbi_opt
fbi_opt = True
global xub
xub = 0

#for each queue check if it is not full
BUF_SIZE = 10

global sniffer_queue
sniffer_queue = Queue.Queue(BUF_SIZE)
global colors
colors = ['green', 'red', 'blue', 'black']

def make_sure_path_exists(path):
	if not os.path.exists(path):
		os.makedirs(path)

starting_time = strftime("%H%M%S", localtime())
starting_day = strftime("%d%m%y", localtime())

pwd = subprocess.check_output(['pwd']).rstrip() + "/"
if "smart_directions_rasp" not in pwd:
	pwd = pwd + "smart_directions_rasp/"

ping_csv_path = pwd+"data/"+starting_day+"/"+starting_time+"/ping_rssi"
session_csv_path = pwd+"data/"+starting_day+"/session_"+starting_time+".csv"

make_sure_path_exists(ping_csv_path)
#make_sure_path_exists(session_csv_path)

rasp_id = subprocess.check_output(['cat', pwd+'config/raspi-number.txt'])[:1]
logging.basicConfig(filename= 'rasp'+rasp_id+'.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug("Start smart directions on rasp "+rasp_id)
logging.debug("directory: "+ pwd)

broker_address = "10.172.0.11" 
broker_address_xub = "10.0.2.15" 
topic_name = "topic/rasp4/directions"

StopMsg = namedtuple('StopMsg', ['mac_address', 'timestamp'])



def signal_handler(signal, frame):
	logging.info("Signal Handler arrived")
	print "Exit!"

	#close all the thread in thread list
	logging.debug("the thread are: %s", t_sniffer)
	print t_sniffer
	
	for user in t_sniffer:
		logging.debug("close thread %s", user[0])
		user[0].stop()
	logging.info("Stop all ping thread")
	
	t_mqtt.stop()
	logging.info("Stop mqtt thread")

	t_proj.stop()
	logging.info("Stop projector thread")

	
	#TODO try catch
	try:
		killall_fbi = subprocess.check_output(['killall', 'fbi'], stderr=subprocess.PIPE)
		logging.debug("Closing fbi process %s", killall_fbi)
	except subprocess.CalledProcessError as e:
		logging.warning(e)
		logging.warning("No fbi process")
	
	try:
		killall_ping = subprocess.check_output(['killall', 'l2ping'], stderr=subprocess.PIPE)
		logging.debug("Closing l2ping process %s", killall_ping)
	except subprocess.CalledProcessError as e:
		logging.warning(e)
		logging.warning("No l2ping process")

	

	logging.info("Closing the timer")
	#close timer
	for t in timer_sniffer:
		t[0].cancel()

	if fbi_opt:
		logging.info("Reopen display")
		subprocess.Popen(['chvt', '9', '&&', 'chvt', '7'], stderr=subprocess.PIPE)

	logging.info("Closing the program")
	sys.exit(0)

def args_parser():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'bfhxv', ['broker=', 'help', 'fbi=','xub=', 'verbose='])
		logging.debug("Input params %s", opts)
	except getopt.GetoptError as err:
		print str(err)
		#logging.warning("params error"+opts)
		#usage()
		print "Error, TODO how to use"
		logging.warning("exit program")
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			logging.debug("help")
			print "TODO how to use"
			#usage()
			logging.info("exit program")
			sys.exit(2)
		elif opt in ('-x', '--xub'):
			#xub = 1
			logging.debug("xub mode enabled %d", xub)
		elif opt in ('-b', '--broker'):
			global broker_address
			broker_address=arg
			logging.debug("mqttt broker set to %s", broker_address)
		elif opt in ('-v', '--verbose'):
			logging.getLogger().setLevel(logging.DEBUG)
			logging.debug("vervose mode enabled %s", opt)
		elif opt in ('-f', '--fbi'):
			global fbi_opt
			fbi_opt = False
			logging.debug("fbi mode disabled %d", fbi_opt)
		else:
			#usage()
			logging.warning("some error in params ",params)
			print "Exit.. TODO how to use"
			logging.info("exit program")
			sys.exit(2)

	return broker_address, " ", fbi_opt

def open_map(map_path):
	logging.info("Opening map")
	tree = ET.parse(map_path)
	root = tree.getroot()
	return root


def is_in_list(mac_addr):
	for t in t_sniffer:
		if mac_addr in t:
			return True
	return False


def stop_single_process(item):
	mac_target, timestamp = item
	
	if is_in_list(mac_target):
		print "stop the process ", mac_target
		logging.info("Stop the process %s", mac_target)
		stop_q = [q for q in stop_list if mac_target in q]
		
		#remove old user
		for usr in stop_list:
			if mac_target in usr:
				logging.info("Remove user %s", usr)
				stop_list.remove(usr)
		
		stop_q = stop_q[0][0]

		stop_q.put(item)

		if mac_target in projector_up:
			#delete user from list and send to projector thread
			logging.info("Delete projector usr %s", mac_target)
			print "del user for inactivity"
			del projector_up[mac_target]
			projector_queue.put(projector_up)
		
		#restore color in list
		color_dismissed = users_colors[mac_target]
		colors.append(color_dismissed)
		color_used.remove(color_dismissed)
		logging.info("Restore color %s", color_dismissed)

	for t in timer_sniffer:
		if mac_target in t:
			t[0].cancel()


def stop_timer(mac_addr, ts):
	print "Stop timer ", mac_addr
	logging.info("Stop timer %s", mac_addr)

	if is_in_list(mac_addr):
		stop_msg = StopMsg(mac_address=mac_addr, timestamp=ts)
		stop_single_process(stop_msg)
		logging.debug("Send stop msg in queue")
	
def assign_color():
	if len(colors)>0:
		color_chosed = colors[0]
		colors.remove(color_chosed)
		color_used.append(color_chosed)
		return color_chosed
	else:
		return "Purple"

def user_color(my_mac):
	for usr in t_sniffer:
		if my_mac in usr:
			return usr[2]
			
	return None

def create_user(my_item, my_mac):
	stop_queue = Queue.Queue(BUF_SIZE)
	stop_list.append([stop_queue, my_mac])
	
	user = PingHandler.PingThread(my_item, map_root, sniffer_queue, stop_queue)
	users_colors[my_mac] = assign_color()

	t_sniffer.append([user, my_mac, users_colors[my_mac]])

	

	logging.debug("Creating a new thread")
	user.start()

	#create timer
	timer = threading.Timer(60.0, stop_timer, [my_mac, datetime.now()])
	timer.start()
	timer_sniffer.append([timer, my_mac])
	logging.info("New user %s!", my_mac) 
				

#### MAIN ####
if __name__ == "__main__":
	logging.info("_____________________________")
	logging.info("SM4RT_D1R3CT10Nz v0.3 thread")
	signal.signal(signal.SIGINT, signal_handler)
	print "SM4RT_D1R3CT10Nz v0.3 thread", rasp_id
	logging.info("Starting main...")
	#setup display
	logging.debug("Killing fbi")
	subprocess.Popen(['killall', 'fbi'], stderr=subprocess.PIPE)

	logging.debug("Opening chvt 9 (black screen)")
	
	args_parser()

	if fbi_opt:
		subprocess.Popen(['chvt', '9'], stderr=subprocess.PIPE)

	if xub:
		broker_address = broker_address_xub
		logging.debug("Set broker address in xub mode: "+ broker_address)

	map_root = open_map('map.xml')
	
	logging.info("the broker_address is "+broker_address)

	#GLOBAL VARS
	global users_colors
	users_colors = {}
	global color_used
	color_used = []

	global projector_up
	projector_up = {}

	global projector_queue
	projector_queue = Queue.Queue(BUF_SIZE)

	mqtt_sub_q = Queue.Queue(BUF_SIZE)
	mqtt_pub_q = Queue.Queue(BUF_SIZE)


	t_mqtt = MqttHandler.MqttThread(mqtt_sub_q, mqtt_pub_q, broker_address)
	t_proj = ProjectorHandler.ProjectorThread(projector_queue, fbi_opt)
	t_mqtt.setDaemon(True)
	t_proj.setDaemon(True)

	t_mqtt.start()
	t_proj.start()
	
	f = open(session_csv_path, 'w')
	f.write("\"id\",\"mac_address\",\"ts_arrive\",\"ts_dep\"")
	f.close()

	timetable = {}

	while True: 
		if not mqtt_sub_q.empty():
			item = mqtt_sub_q.get()
			logging.info("A new message is arrived.")
			logging.info(item)
			print "new message is arrived"

			if type(item).__name__ == "StartMsg":
				logging.info("The type is START MSG")
				logging.debug("Message content %s", item)
				mac_thread = item[0]
				print "The type is START MSG with mac ", mac_thread 
				
				if len(t_sniffer) > 0:
					if not [s for s in t_sniffer if mac_thread in s[1]]:
						create_user(item, mac_thread)
					else:
						logging.debug("user %s is already present", mac_thread)

				else:
					create_user(item, mac_thread)


			elif type(item).__name__ == "StopMsg":
				logging.info("The type is STOP MSG %s", item)
				print "STOP MESSAGE", item
				
				stop_single_process(item)
				

		if not sniffer_queue.empty():
			proj_msg = sniffer_queue.get()
			logging.info("A projector msg is arrived")
			logging.debug("Reading proj queue msg: %s", proj_msg)

			if type(proj_msg).__name__ == "ProjMsg":
				logging.debug("The type is proj_msg")
				mac_target, direction, new_proj_status, final_pos, timestamp = proj_msg
				logging.debug("mac %s, dir: %s, new_proj_statu: %s, final: %s", mac_target, direction, new_proj_status, final_pos)

				if is_in_list(mac_target):
					
					if new_proj_status:

						logging.info("New image")
						if mac_target not in projector_up:
							projector_up[mac_target] = [direction, user_color(mac_target)]
							print projector_up
							projector_queue.put(projector_up)

					if not new_proj_status:
						logging.info("Remove an image")
						del projector_up[mac_target]
						print projector_up
						projector_queue.put(projector_up)
					

					if final_pos:
						print "The user is arrived to the final step, sending msg to the other sniffers..."
						logging.info("The user is in the final step")
						time.sleep(15)
						logging.info("Sending msg to the others sniffers")
						mqtt_pub_q.put(mac_target)

		t_sniffer = [t for t in t_sniffer if t[0].is_alive()]

