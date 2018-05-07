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
import xml.etree.ElementTree as ET
import pprint as pp
from collections import namedtuple
#my imports
import MqttHandler
import PingHandler


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

global sniffer_queue
sniffer_queue = Queue.Queue()
global colors
colors = ['Green', 'Red', 'Blue', 'Black']



StopMsg = namedtuple('StopMsg', ['mac_address', 'timestamp'])
pwd = subprocess.check_output(['pwd']).rstrip() + "/"
rasp_id = subprocess.check_output(['cat', pwd+'config/raspi-number.txt'])[:1]
logging.basicConfig(filename= 'rasp'+rasp_id+'.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug("Start smart directions on rasp "+rasp_id)
logging.debug("directory: "+ pwd)

broker_address = "192.168.1.3" 
broker_address_xub = "10.0.2.15" 
topic_name = "topic/rasp4/directions"


def signal_handler(signal, frame):
	logging.info("Signal Handler arrived")
	print "Exit!"

	#close all the thread in thread list
	logging.debug("the thread are: %s", t_sniffer)
	print t_sniffer
	
	for user in t_sniffer:
		logging.debug("closing thread %s", user[0])
		user[0].stop()
	logging.info("stopping all ping thread")
	
	t_mqtt.stop()
	logging.info("Stopping mqtt thread")

	#TODO try catch
	try:
		killall_fbi = subprocess.check_output(['killall', 'fbi'], stderr=subprocess.PIPE)
		logging.debug("Closing fbi process %s", killall_fbi)
	except subprocess.CalledProcessError as e:
		logging.warning(e)
		logging.warning("No fbi process")
	
	subprocess.Popen(['xset', 'dpms', 'force', 'on'], stderr=subprocess.PIPE)
	
	try:
		killall_ping = subprocess.check_output(['killall', 'l2ping'], stderr=subprocess.PIPE)
		logging.debug("Closing l2ping process %s", killall_ping)
	except subprocess.CalledProcessError as e:
		logging.warning(e)
		logging.warning("No l2ping process")

	logging.info("Closing the program")


	#close timer
	for t in timer_sniffer:
		t[0].cancel()

	sys.exit(0)

def args_parser():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'fhxv', ['help', 'fbi=','xub=', 'verbose='])
		logging.debug("Input params %s", opts)
	except getopt.GetoptError as err:
		print str(err)
		#logging.warning("params error"+opts)
		#usage()
		print "Error, TODO how to use"
		logging.warning("exit program")
		sys.exit(2)

	global xub
	global fbi_opt
	fbi_opt = 1
	xub = 0

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			logging.debug("help")
			print "TODO how to use"
			#usage()
			logging.info("exit program")
			sys.exit(2)
		elif opt in ('-x', '--xub'):
			xub = 1
			logging.debug("xub mode enabled %d", xub)
		elif opt in ('-v', '--verbose'):
			logging.getLogger().setLevel(logging.DEBUG)
			logging.debug("vervose mode enabled %s", opt)
		elif opt in ('-f', '--fbi'):
			fbi_opt = 0
			logging.debug("fbi mode disabled %d", fbi_opt)
		else:
			#usage()
			logging.warning("some error in params ",params)
			print "Exit.. TODO how to use"
			logging.info("exit program")
			sys.exit(2)


def display_image(my_direction):
	arrow_path = "arrows/Green_arrow_"+my_direction+".png"

	print "show image"
	if fbi_opt:
		logging.info("Shows image")
		logging.debug("Direction: %s", my_direction)
		logging.debug("Image path: %s", arrow_path)
	
		

		logging.info("Displaying image")
		proj_proc = subprocess.Popen(['fbi','-a', '--noverbose', '-T', '1', arrow_path], stderr=subprocess.PIPE, shell=False)
		print "pid:", proj_proc.pid()

def turn_off_screen():
	proj_status = False
	print "Turning off the screen"
	logging.info("Turning off the screen")
	logging.info("Killing fbi")
	subprocess.Popen(['killall', 'fbi'])
	logging.info("Closing tvservice (turn off the screen)")
	#subprocess.Popen(['tvservice', '-o'])
	subprocess.Popen(['xset', 'dpms', 'force', 'on'], stderr=subprocess.PIPE)

def opening_map(map_path):
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
	logging.debug("Stop the process %s", mac_target)

	if is_in_list(mac_target):
		correct_q = [q for q in stop_list if mac_target in q]
		correct_q = correct_q[0][0]
		correct_q.put(item)
		proj_status = False
		close_proj = True
		turn_off_screen()
		#restore color in list
		color_dismissed = users_colors[mac_target]
		colors.append(color_dismissed)
		color_used.remove(color_dismissed)

	for t in timer_sniffer:
		if mac_target in t:
			t[0].cancel()

def stop_timer(mac_addr):
	print "Stop timer"
	logging.debug("Stop timer")

	if is_in_list(mac_addr):
		#mqtt_pub_q.put(mac_addr)
		stop_msg = StopMsg(mac_address=mac_addr, timestamp="10:21:21")
		stop_single_process(stop_msg)
	
def assign_color():
	if len(colors)>0:
		color_chosed = colors[0]
		colors.remove(color_chosed)
		color_used.append(color_chosed)
		return color_chosed
	else:
		return "Purple"



def create_user(my_item, my_mac):
	stop_queue = Queue.Queue()
	stop_list.append([stop_queue, my_mac])

	user = PingHandler.PingThread(my_item, map_root, sniffer_queue, stop_queue)
	users_colors[my_mac] = assign_color()

	t_sniffer.append([user, my_mac, users_colors[my_mac]])
	print t_sniffer		

	logging.debug("Creating a new thread")
	user.start()

	#create timer
	timer = threading.Timer(60.0, stop_timer, [my_mac])
	timer.start()
	timer_sniffer.append([timer, my_mac]) 
				
	proj_status = False

#### MAIN ####
if __name__ == "__main__":
	logging.info("_____________________________")
	logging.info("SM4RT_D1R3CT10Nz v0.3 thread")
	signal.signal(signal.SIGINT, signal_handler)
	print "SM4RT_D1R3CT10Nz v0.3 thread", rasp_id
	logging.info("Starting main...")
	#setup display
	logging.info("Killing fbi")
	subprocess.Popen(['killall', 'fbi'], stderr=subprocess.PIPE)

	logging.info("Opening tvservice (turn on the screen)")
	#subprocess.Popen(['tvservice', '-p'], stderr=subprocess.PIPE)
	subprocess.Popen(['xset', 'dpms', 'force', 'on'], stderr=subprocess.PIPE)
	
	#subprocess.Popen(['tvservice', '-p'])
	#logo_path = 'arrows/smart_dir_logo.png'
	#subprocess.Popen(['fbi','-a', '--noverbose', '-T', '1', logo_path])
	args_parser()

	if xub:
		broker_address = broker_address_xub
		logging.debug("Set broker address in xub mode: "+ broker_address)

	map_root = opening_map('map.xml')
	
	logging.info("the broker_address is "+broker_address)

	global users_colors
	users_colors = {}
	global color_used
	color_used = []
	

	mqtt_sub_q = Queue.Queue()
	mqtt_pub_q = Queue.Queue()


	t_mqtt = MqttHandler.MqttThread(mqtt_sub_q, mqtt_pub_q, broker_address)
	t_mqtt.setDaemon(True)
	logging.info("Setting up the mqtt thread")


	t_mqtt.start()
	


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
						print "user is already present"

				else:
					create_user(item, mac_thread)


			elif type(item).__name__ == "StopMsg":
				logging.info("The type is STOP MSG")
				logging.debug("Message content %s", item)
				print "the type is STOP MESSAGE"
				
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
					if not proj_status:# and not close_proj:
						logging.debug("if the status if off (%s)", proj_status)
						if new_proj_status:
							logging.debug("the new status is on (%s)", new_proj_status)
							display_image(direction)
							proj_status = new_proj_status
					elif proj_status:
						logging.debug("if the status if on (%s)", proj_status)
						if not new_proj_status:
							logging.debug("the new status is OFF (%s)", new_proj_status)
							proj_status = new_proj_status
							turn_off_screen()

					if final_pos:
						print "user is arrived to the final step, sending msg to the other sniffers"
						logging.info("The user is in the final step")
						time.sleep(15)
						logging.info("Sending msg to the others sniffers")
						mqtt_pub_q.put(mac_target)
						#turn_off_screen()
						#proj_status = False
						print t_sniffer

		t_sniffer = [t for t in t_sniffer if t[0].is_alive()]

