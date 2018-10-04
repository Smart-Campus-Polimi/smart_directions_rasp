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

	#kind of absolute path
	pwd = os.path.expanduser('~/smart_directions_rasp/')
	#create path for files....
	ping_csv_path = pwd+"data/"+_starting_day+"/"+_starting_time+"/ping_rssi" 

	_create_session_csv(_starting_day, _starting_time, pwd)

	_make_sure_path_exists(ping_csv_path)

	#save rasp_id from raspi-number file (A, B, C...)
	rasp_id = subprocess.check_output(['cat', pwd+'config/raspi-number.txt'])[:1] 
	global LOG_FILE
	LOG_FILE = pwd+'rasp'+rasp_id+'.log'


	c.logging.debug("Start smart directions on rasp "+rasp_id)
	c.logging.debug("directory: "+ pwd)

	return rasp_id, pwd