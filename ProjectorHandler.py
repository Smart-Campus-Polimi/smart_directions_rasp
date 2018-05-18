#!/usr/bin/python

import logging
import threading
import Queue
import subprocess
import sys
import os
import errno

import thread_test

#sx
#dx
#down
#up

def kill_pid(pid):

    if pid < 0:
        return False
    if pid == 0:
        # According to "man 2 kill" PID 0 refers to every process
        # in the process group of the calling process.
        # On certain systems 0 is a valid PID but we have no way
        # to know that in a portable fashion.
        raise ValueError('invalid PID 0')
    try:
    	print "kill ", pid
        os.kill(pid, 9)
    except OSError as err:
        if err.errno == errno.ESRCH:
            # ESRCH == No such process
            return False
        elif err.errno == errno.EPERM:
            # EPERM clearly means there's a process to deny access to
            return True
        else:
            # According to "man 2 kill" possible error values are
            # (EINVAL, EPERM, ESRCH)
            raise
    else:
        return True

def kill_process():
	fbi_process = subprocess.check_output(['sh', 'check_process_running.sh', 'fbi'])
	fbi_process = fbi_process.split()
	for p in fbi_process:
		kill_pid(int(p))

def projector(my_indication,my_num, vis_active):
	if my_indication:
		count = 0
		path = []
		for key, value in my_indication.iteritems():
			count += count
			path.append("arrows/"+value[1]+"/"+value[0]+".png")

		out_path = 'arrows/out/my_direction'+str(my_num)+'.png'
		
		subprocess.check_output(['montage', '-geometry', '1280x960+2+2', '-tile', str(count)+'x'+str(count)] + path + [out_path], stderr=subprocess.PIPE)

		kill_process()
		print "project, new path: ", out_path
		
		if vis_active:
			print "proj", thread_test.fbi_opt
			subprocess.Popen(['fbi','-a', '--noverbose', '-T', '1', out_path], stderr=subprocess.PIPE)

		
	else:
		try: 
			print "killall"
			subprocess.Popen(['killall', 'fbi'], stderr=subprocess.PIPE)
			kill_process()
			if vis_active:
				print "proj", thread_test.fbi_opt
				subprocess.Popen(['chvt', '9'], stderr=subprocess.PIPE)

		except subprocess.CalledProcessError as e:
			pass

class ProjectorThread(threading.Thread):
	def __init__(self, queue, proj_active):
		threading.Thread.__init__(self)
		self.queue = queue
		self.proj_active = proj_active


	def run(self):
		visual = {}
		num = 0
		new_img = False
		self.is_running = True
		while self.is_running:
			if not self.queue.empty():
				visual = self.queue.get()
				new_img = True

			if new_img:
				num = num+1
				projector(visual,num, self.proj_active)
				new_img = False



	def stop(self):
		#close proj processes
		kill_process()
		self.is_running = False
			
