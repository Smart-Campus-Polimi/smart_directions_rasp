#!/usr/bin/python

import subprocess
import logging
import os

#for each queue check if it is not full
BUF_SIZE = 10
BROKER_ADDRESS = "10.79.5.210" #server address 
BROKER_ADDRESS_LOCAL = "10.0.2.15" #localhost
TOPIC_LIST = ["new_user", "stop_ping"] #mqtt_topic
PWD = os.path.expanduser('~/smart_directions_rasp/')
MAP = PWD+'config/map.xml'
RASP_ID = subprocess.check_output(['cat', PWD+'config/raspi-number.txt'])[:1] 

logging.basicConfig(filename= PWD+'log.txt',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
