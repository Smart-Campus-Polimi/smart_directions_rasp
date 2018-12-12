#!/usr/bin/python

######## Prepare the folder environment to store and retrieve data ########
import subprocess
import os
import constants as c
from time import strftime, localtime



global LOG_FILE

#### FUNCTIONS ####
#path to a folder
def _make_sure_path_exists(path):
	if not os.path.exists(path):
		os.makedirs(path)

def _create_session_csv(day, time, pwd):
	session_csv_path = pwd+"data/"+day+"/session_"+time+".csv"
	f = open(session_csv_path, 'w')
	f.write("\"id\",\"mac_address\",\"ts_arrive\",\"ts_dep\"")
	f.close()

def create_path_and_files():
	_starting_time = strftime("%H%M%S", localtime()) #hour, minute, second
	_starting_day = strftime("%d%m%y", localtime()) #day, month, year

	#create path for files....
	ping_csv_path = c.PWD+"data/"+_starting_day+"/"+_starting_time+"/ping_rssi" 

	_create_session_csv(_starting_day, _starting_time, c.PWD)

	_make_sure_path_exists(ping_csv_path)

	#save rasp_id from raspi-number file (A, B, C...)
	rasp_id = subprocess.check_output(['cat', c.PWD+'config/raspi-number.txt'])[:1] 
	global LOG_FILE
	LOG_FILE = c.PWD+'rasp'+c.RASP_ID+'.log'


	c.logging.debug("Start smart directions on rasp "+rasp_id)
	c.logging.debug("directory: "+ c.PWD)

	return rasp_id