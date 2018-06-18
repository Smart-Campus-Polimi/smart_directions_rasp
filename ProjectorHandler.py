#!/usr/bin/python

import logging
import threading
import Queue
import subprocess
import sys
import os
import errno

import thread_test

global projector_queue

### PYGLET CLASS
from pyglet.gl import *


global my_indication, my_color
my_indication = {}
my_color = []


#### ARROWS
o_x = .0
o_y = .0
offset = .15
offset_thick = .05  


sx = [	o_x-.2,     o_y,        .0, 
		o_x+.0,     o_y+.5,     .0,
		o_x+.1,     o_y+.5,     .0,
		o_x-.1,     o_y,        .0,
		o_x+.1,     o_y-.5,     .0,
		o_x,        o_y-.5,     .0]

dx = [		(o_x+.2),                   -(o_y),                .0,
			(o_x+.0),                   -(o_y+.5 -offset),     .0,
			(o_x-.1),                   -(o_y+.5 -offset),     .0,
			(o_x+.1),                   -(o_y),                .0,
			(o_x-.1),                   -(o_y-.5 +offset),     .0,
			(o_x),                      -(o_y-.5 +offset),     .0]
		
down = [	-(o_y),               +(o_x-.2),                  .0, 
			-(o_y+.5 -offset),    +(o_x+.0),                  .0,
			-(o_y+.5 -offset),    +(o_x+.1+offset_thick),     .0,
			-(o_y),               +(o_x-.1+offset_thick),     .0,
			-(o_y-.5 +offset),    +(o_x+.1+offset_thick),     .0,
			-(o_y-.5 +offset),    +(o_x),                     .0]

up = [		+(o_y),               -(o_x-.2),                  .0, 
			+(o_y+.5 -offset),    -(o_x+.0),                  .0,
			+(o_y+.5 -offset),    -(o_x+.1+offset_thick),     .0,
			+(o_y),               -(o_x-.1+offset_thick),     .0,
			+(o_y-.5 +offset),    -(o_x+.1+offset_thick),     .0,
			+(o_y-.5 +offset),    -(o_x),                     .0] 

####COLORS
blue = [0,0,205, 0,0,205, 30,144,255, 0,0,205, 0,0,205, 0,0,205]
red = [139,0,0, 240,128,128, 139,0,0, 139,0,0, 139,0,0, 139,0,0]
white = [255,255,240, 255,255,240, 248,248,255, 255,255,240, 255,255,240, 255,255,240]
green = [34,139,34, 50,205,50, 34,139,34, 34,139,34, 34,139,34, 34,139,34]


indications = {'up': up, 
			   'down': down,
			   'sx': sx,
			   'dx': dx }

colors = {'blue': blue,
		  'red': red,
		  'white': white,
		  'green': green  }

def move_arrow_left(arrow):
    new_pos = []
    for coord in range(0,len(arrow)):
        my_pos = float(arrow[coord])
        if coord % 3 == 0:
            my_pos = my_pos - 0.6
            my_pos = float("{0:.2f}".format(my_pos))
        new_pos.append(float(my_pos))
    return new_pos

def move_arrow_right(arrow):
    new_pos = []
    for coord in range(0,len(arrow)):
        my_pos = float(arrow[coord])
        if coord % 3 == 0:
            my_pos = my_pos + 0.6
            my_pos = float("{0:.2f}".format(my_pos))
        new_pos.append(float(my_pos))

    return new_pos

def move_arrow_down(arrow):
    new_pos = []
    for coord in range(0,len(arrow)):
        my_pos = float(arrow[coord])
        if (coord % 3) == 1:
            my_pos = my_pos - 0.6
            my_pos = float("{0:.2f}".format(my_pos))
        new_pos.append(float(my_pos))

    return new_pos

def move_arrow_up(arrow):
    new_pos = []
    for coord in range(0,len(arrow)):
        my_pos = float(arrow[coord])
        if (coord % 3) == 1:
            my_pos = my_pos + 0.6
            my_pos = float("{0:.2f}".format(my_pos))
        new_pos.append(float(my_pos))

    return new_pos

def draw_fig(indic, cols):
	figures = []


	global my_indication
	j = 0
	for key, value in my_indication.iteritems():
		if len(my_indication) == 1:
			print_arr = indications[value[0]]

		if len(my_indication) == 2:
			if j == 0:
				print_arr = move_arrow_right(indications[value[0]])
			if j == 1:
				print_arr = move_arrow_left(indications[value[0]])
			j = j+ 1
			

		if len(my_indication) == 3:
			if j == 0:
				print_arr = move_arrow_up(move_arrow_right(indications[value[0]]))
			if j == 1:
				print_arr = move_arrow_up(move_arrow_left(indications[value[0]]))
			if j == 2:
				print_arr = move_arrow_down(indications[value[0]])
			j = j+ 1
			

		if len(my_indication) == 4:
			if j == 0:
				print_arr = move_arrow_up(move_arrow_right(indications[value[0]]))
			if j == 1:
				print_arr = move_arrow_up(move_arrow_left(indications[value[0]]))
			if j == 2:
				print_arr = move_arrow_down(move_arrow_right(indications[value[0]]))
			if j == 3:
				print_arr = move_arrow_down(move_arrow_left(indications[value[0]]))
			
			j = j+ 1
			

		vertices = pyglet.graphics.vertex_list(6, ('v3f',print_arr),
											  ('c3B', colors[value[1]]))
		
		figures.append(vertices)

	for fig in figures:
		fig.draw(pyglet.gl.GL_POLYGON)

class MyWindow(pyglet.window.Window):
		def __init__(self, *args, **kwargs):
			super(MyWindow, self).__init__(*args, **kwargs)
			self.set_minimum_size(400,300)
			glClearColor(0, 0, 0, 0)
			pyglet.clock.schedule_interval(self.update, 5.0/24.0)
			self.visual = {}

			

		def on_draw(self):
			self.clear()
			global my_indication, my_color
			draw_fig(my_indication, my_color)
		
		def update(self, dt):
			if not projector_queue.empty():
				print "there's a new proj command"
				self.visual = projector_queue.get()

				print "visual", self.visual

				global my_indication, my_color
				my_indication = self.visual

		def on_resize(self, width, height):
			glViewport(0, 0, width, height)



class ProjectorThread(threading.Thread):
	def __init__(self, queue, proj_active):
		threading.Thread.__init__(self)
		global projector_queue
		projector_queue = queue
		self.proj_active = proj_active
		

	def run(self):

		window = MyWindow(1024, 768, "test directionsolo", resizable=False, visible=True, fullscreen=False)
		pyglet.app.run()


	def stop(self):
		self.is_running = False
			
