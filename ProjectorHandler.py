#!/usr/bin/python

import logging
import threading
import Queue
import subprocess
import sys
import os
import errno
import my_main
import copy

global projector_queue

### PYGLET CLASS
from pyglet.gl import *


global indications
indications = {}


#### ARROWS
window_width = 1024
window_height = 768

offset = .10
height = .75
width = .3
rapp1 = float(window_width)/float(window_height)
rapp2 = float(window_height)/float(window_width)


sx = [[	-width/2+offset,    0,             0,
		 width/2,           height/2,      0,
		 width/2-offset,    height/2,      0,
		-width/2,           0,             0,
		 width/2-offset,   -height/2,      0,
		 width/2,          -height/2,      0]]

dx = [[   width/2-offset,    0,             0,
		-width/2,           height/2,      0,
		-width/2+offset,    height/2,      0,
		 width/2,           0,             0,
		-width/2+offset,   -height/2,      0,
		-width/2,          -height/2,      0]]


up = [[  0*rapp2,   		 -(-width/2+offset)*rapp1,        0,
		(+height/2)*rapp2,   -(width/2)*rapp1,                0,
		(+height/2)*rapp2,   -(width/2-offset)*rapp1,         0,
				  0*rapp2,   -(-width/2)*rapp1,               0,
		(-height/2)*rapp2,   -(width/2-offset)*rapp1,         0,
		(-height/2)*rapp2,   -(width/2)*rapp1,                0]]

down = [[0*rapp2,   		 +(-width/2+offset)*rapp1,        0,
		(+height/2)*rapp2,   +(width/2)*rapp1,                0,
		(+height/2)*rapp2,   +(width/2-offset)*rapp1,         0,
				  0*rapp2,   +(-width/2)*rapp1,               0,
		(-height/2)*rapp2,   +(width/2-offset)*rapp1,         0,
		(-height/2)*rapp2,   +(width/2)*rapp1,                0]]


####COLORS
cyan = [0,171,255, 0,171,255, 0,171,255, 0,171,255, 0,171,255, 0,171,255]
yellow = [255,255,0, 255,255,0, 255,255,0, 255,255,0, 255,255,0, 255,255,0]
white = [255,255,255, 255,255,255, 255,255,255, 255,255,255, 255,255,255, 255,255,255]
green = [51,255,51, 51,255,51, 51,255,51, 51,255,51, 51,255,51, 51,255,51]

colors = {'cyan': cyan,
		  'yellow': yellow,
		  'white': white,
		  'green': green  }


def scale_figure(my_figure, scaling):
	new_fig = []
	for item in my_figure:
		half_fig = []
		for coord in item:
			half_fig.append(coord*scaling)
		new_fig.append(half_fig)
	return new_fig


def draw_go_back():
	mini_offset = .05

	right_back = [(+width/2),			 (+height/2),			   0,
				  (+width/2)+mini_offset,(+height/2),			   0,
				  (+width/2)+mini_offset,(-height/2)+mini_offset*2,0,
				  (+width/2),			 (-height/2)+mini_offset*2,0]

	left_back = [-(+width/2),			 (+height/2),			 0,
			     -(+width/2)+mini_offset,(+height/2),			 0,
			     -(+width/2)+mini_offset,(-height/2)+mini_offset,0,
			     -(+width/2),			 (-height/2)+mini_offset,0]
	
	up_back = [(-width/2),(+height/2), 0,
			   (+width/2),(+height/2), 0,
			   (+width/2),(+height/2)-mini_offset, 0,
			   (-width/2),(+height/2)-mini_offset, 0,]

	down_back = down[:]
	down_back = scale_figure(down_back, 0.65)
	down_back = move_arrow(down_back, -0.22, False)
	down_back = move_arrow(down_back, -0.1185, True)
	

	return [up_back] + [left_back] + [right_back] + down_back


###### END ARROWS #####


### FUNCTIONS ###
def update_coordinates(my_indications):
	j = 0
	for key, value in my_indications.iteritems():
		if len(my_indications) == 1:
			my_indications[key].append(arrows[value[0]])
		if len(my_indications) == 2:
			if j == 0:
				my_indications[key].append(move_arrow_right(arrows[value[0]]))
			if j == 1:
				my_indications[key].append(move_arrow_left(arrows[value[0]]))

		if len(my_indications) == 3:
			if j == 0:
				my_indications[key].append(move_arrow_up(move_arrow_right(arrows[value[0]])))
			if j == 1:
				my_indications[key].append(move_arrow_up(move_arrow_left(arrows[value[0]])))
			if j == 2:
				my_indications[key].append(move_arrow_down(arrows[value[0]]))

		if len(my_indications) == 4:
			if j == 0:
				my_indications[key].append(move_arrow_up(move_arrow_right(arrows[value[0]])))
			if j == 1:
				my_indications[key].append(move_arrow_up(move_arrow_left(arrows[value[0]])))
			if j == 2:
				my_indications[key].append(move_arrow_down(move_arrow_right(arrows[value[0]])))
			if j == 3:
				my_indications[key].append(move_arrow_down(move_arrow_left(arrows[value[0]])))

		j += 1

	return my_indications

def move_arrow(my_arrow, offset, horiz):
	new_pos = []

	if horiz:
		flag = 0
	else:
		flag = 1

	i = 0
	for piece in my_arrow:
		single_pos = []
		for coord in piece:
			my_pos = float(coord)
			if i % 3 == flag:
				my_pos = float(my_pos) + float(offset)
				my_pos = float("{0:.2f}".format(my_pos))
			single_pos.append(float(my_pos))
			i += 1
		new_pos.append(single_pos)

	return new_pos

def move_arrow_horiz(my_arrow, offset):
	return move_arrow(my_arrow, offset, horiz=True)

def move_arrow_vertic(my_arrow, offset):
	return move_arrow(my_arrow, offset, horiz=False)

def move_arrow_left(arrow):
	return move_arrow_horiz(arrow, -.6)

def move_arrow_right(arrow):
	return move_arrow_horiz(arrow, +.6)
   
def move_arrow_down(arrow):
	return move_arrow_vertic(arrow, -.6)

def move_arrow_up(arrow):
	return move_arrow_vertic(arrow, +.6)

def draw_fig(my_indications):
	

	figures = []

	for key, value in my_indications.iteritems():
		for v in value[2]:
			fig = pyglet.graphics.vertex_list(len(v)/3, ('v3f', v), ('c3B', colors[value[1]][:len(v)]))
			figures.append(fig)

	return figures
	

def check_new_arrows(): 
	if not projector_queue.empty():
		global indications
		indications = copy.deepcopy(projector_queue.get())
		print "new indication is arrived: ", indications

		if indications:
			indications = update_coordinates(indications)

def animate_arrow(my_indications, moving):
	for key, value in my_indications.iteritems():
		if 'up' in value[0]:
			horiz = False
			my_offset = +.2
			if moving == 1:
				my_offset = -.6
		if 'down' in value[0]:
			horiz = False
			my_offset = -.2
			if moving == 1:
				my_offset = +.6
		if 'sx' in value[0]:
			horiz = True
			my_offset = -.2
			if moving == 1:
				my_offset = +.6
		if 'dx' in value[0]:
			my_offset = .2
			if moving == 1:
				my_offset = -.6
			horiz = True

		if 'back' in value[0]:
			if moving%2 == 0:
				my_offset = -20
			else: 
				my_offset = +20
			horiz = True

		value[2] = move_arrow(value[2], my_offset, horiz)

	return my_indications

def update_moving(my_mov):
	my_mov += 1
	if my_mov == +2:
		my_mov = -2
	return my_mov
### END FUNCTIONS ###
	
arrows = {'sx': sx,
		  'dx': dx,
		  'up': up,
		  'down': down,
		  'back': draw_go_back()
		  }

class MyWindow(pyglet.window.Window):
		def __init__(self, *args, **kwargs):
			super(MyWindow, self).__init__(*args, **kwargs)
			self.set_minimum_size(400,300)
			glClearColor(0, 0, 0, 0)
			pyglet.clock.schedule_interval(self.update, 7.0/24.0)
			self.moving = 0

			

		def on_draw(self):
			self.clear()
			global figures
			figures = draw_fig(indications)
			#fig = pyglet.graphics.vertex_list(6, ('v3f', arrows['dx']), ('c3B', blue))
			for fig in figures:
				fig.draw(pyglet.gl.GL_POLYGON)
		
		def update(self, dt):
			#retrieve arrows from the queue (from main)
			check_new_arrows()
			#move the arrows
			animate_arrow(indications, self.moving)
			self.moving = update_moving(self.moving)
			
			


		def on_resize(self, width, height):
			glViewport(0, 0, width, height)



class ProjectorThread(threading.Thread):
	def __init__(self, queue, proj_active):
		threading.Thread.__init__(self)
		global projector_queue
		projector_queue = queue
		#self.proj_active = proj_active ##NOT USED!!!
		

	def run(self):
		window = MyWindow(window_width, window_height, "test directions", resizable=False, visible=True, fullscreen=True)
		pyglet.app.run()


	def stop(self):
		self.is_running = False
			
