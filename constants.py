#!/usr/bin/python

import logging
import os

#for each queue check if it is not full
BUF_SIZE = 10
BROKER_ADDRESS = "10.79.1.176" #server address 
BROKER_ADDRESS_LOCAL = "10.0.2.15" #localhost
TOPIC_LIST = ["topic/rasp4/directions", "stop_ping]" #mqtt_topic
PWD = os.path.expanduser('~/smart_directions_rasp/')
MAP = PWD+'config/map.xml'


logging.basicConfig(filename= PWD+'log.txt',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
