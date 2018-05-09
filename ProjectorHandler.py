#!/usr/bin/python

import logging
import threading
import Queue

import thread_test


def projector(my_indication):
	if not my_indication:
		#printa quello che devo printare
	else:
		#turn off screen

class ProjectorThread(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue

	def run(self):
		self.is_running = True
		while self.is_running:
			if not self.queue.empty():
				visual = self.queue.get()
				print visual

			projector(visual)



	def stop(self):
		self.is_running = False
		#close proj processes