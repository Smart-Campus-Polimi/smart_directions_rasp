#!/usr/bin/python

import logging

#for each queue check if it is not full
BUF_SIZE = 10
BROKER_ADDRESS = "10.79.1.176" #server address 
BROKER_ADDRESS_LOCAL = "10.0.2.15" #localhost
TOPIC_NAME = "topic/rasp4/directions" #mqtt_topic


logging.basicConfig(filename= 'log.txt',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
