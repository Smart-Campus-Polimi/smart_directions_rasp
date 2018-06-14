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

global projector_queue

### PYGLET CLASS
from pyglet.gl import *
from draw_arrows import DrawArrows


empty = [0.0,0.0,0.0, 0.0,0.0,0.0, 0.0,0.0,0.0]
global my_indication, my_color
my_indication = []
my_color = []

up = [-0.5,-0.5,0.0, 0.5,-0.5,0.0, 0.0,0.5,0.0]
down = [0.5,0.5,0.0, -0.5,0.5,0.0, 0.0,-0.5,0.0]
up_dx = [-0.5,0.5,0.0, 0.0,0.5,0.0, -0.5,-0.5,0.0]
sx = [-0.3,0.0,0.0, 0.5,0.5,0.0, 0.5,-0.5,0.0]
dx = [0.3,0.0,0.0, -0.5,0.5,0.0, -0.5,-0.5,0.0]

blue = [0,0,205, 0,0,205, 30,144,255]
red = [139,0,0, 240,128,128, 139,0,0]
white = [255,255,240, 255,255,240, 248,248,255]
green = [34,139,34, 50,205,50, 34,139,34]


indications = {'up': up, 
			   'down': down,
			   'sx': sx,
			   'dx': dx }

colors = {'blue': blue,
		  'red': red,
		  'white': white,
		  'green': green  }


def mod_arrows(to_cast):
	ind = []
	col = []
	if to_cast:
		for key, value in to_cast.iteritems():
			ind.append(indications[value[0]])
			col.append(colors[value[1]])

		return ind, col
	else:
		return ind, col


def draw_fig(inds, cols):
	print "inds, col", inds, cols
	for indic in inds:
		vertices = pyglet.graphics.vertex_list(3, ('v3f', indic),
											  ('c3B', green))
		vertices.draw(pyglet.gl.GL_TRIANGLES)

class MyWindow(pyglet.window.Window):
		def __init__(self, *args, **kwargs):
			super(MyWindow, self).__init__(*args, **kwargs)
			self.set_minimum_size(400,300)
			glClearColor(0, 0, 0, 0)
			pyglet.clock.schedule_interval(self.update, 1.0/24.0)
			self.visual = {}

			

		def on_draw(self):
			self.clear()
			global my_indication, my_color
			draw_fig(my_indication, my_color)
		
		def update(self, dt):

			if not projector_queue.empty():
				print "there's a new proj command"
				self.visual = projector_queue.get()

				global my_indication, my_color
				my_indication, my_color = mod_arrows(self.visual)
				new_img = True


		def on_resize(self, width, height):
			glViewport(0, 0, width, height)



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
			print key, value
			count += count
			path.append("arrows/"+value[1]+"/"+value[0]+".png")

		out_path = 'arrows/out/my_direction'+str(my_num)+'.png'
		
		subprocess.check_output(['montage', '-geometry', '1280x960+2+2', '-tile', str(count)+'x'+str(count)] + path + [out_path], stderr=subprocess.PIPE)

		kill_process()
		print "project, new path: ", out_path
		
		if vis_active:
			#print "proj", thread_test.fbi_opt
			subprocess.Popen(['fbi','-a', '--noverbose', '-T', '1', out_path], stderr=subprocess.PIPE)

		
	else:
		try: 
			print "killall"
			#subprocess.Popen(['killall', 'fbi'], stderr=subprocess.PIPE)
			kill_process()
			if vis_active:
				subprocess.Popen(['fbi','-a', '--noverbose', '-T', '1', 'arrows/bkgnd_black.jpg'], stderr=subprocess.PIPE)
				#print "proj", thread_test.fbi_opt
				#subprocess.Popen(['chvt', '9'], stderr=subprocess.PIPE)

		except subprocess.CalledProcessError as e:
			pass

class ProjectorThread(threading.Thread):
	def __init__(self, queue, proj_active):
		threading.Thread.__init__(self)
		global projector_queue
		projector_queue = queue
		self.proj_active = proj_active
		window = MyWindow(1280, 720, "test directions", resizable=False, visible=True, fullscreen=False)
		


	def run(self):

		pyglet.app.run()


		'''
		visual = {}
		num = 0
		new_img = False
		self.is_running = True
		while self.is_running:
			if not self.queue.empty():
				print "there's a new proj command"
				visual = self.queue.get()
				print "i project ", visual
				new_img = True
				num = num+1
				projector(visual,num, self.proj_active)

			if new_img:
				
				new_img = False

		'''

	def stop(self):
		#close proj processes
		kill_process()
		self.is_running = False
			
