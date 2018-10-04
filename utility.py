#!/usr/bin/python
import getopt
import sys #used?
import xml.etree.ElementTree as ET
import constants as c



def args_parser():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'bhv', ['broker=', 'help', 'verbose='])
		c.logging.debug("Input params %s", opts)
	except getopt.GetoptError as err:
		c.logging.warning("params error"+opts+err)
		#usage() #create a function
		print "Error, TODO how to use"
		c.logging.warning("exit program")
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			c.logging.debug("help")
			print "TODO how to use"
			#usage()
			c.logging.info("exit program")
			sys.exit(2)

		elif opt in ('-b', '--broker'):
			c.BROKER_ADDRESS=arg
			c.logging.debug("mqttt broker set to %s", c.BROKER_ADDRESS)
		elif opt in ('-v', '--verbose'):
			c.logging.getLogger().setLevel(c.logging.DEBUG)
			c.logging.debug("vervose mode enabled %s", opt)
		else:
			#usage()
			c.logging.warning("some error in params ",params)
			print "Exit.. TODO how to use"
			c.logging.info("exit program")
			sys.exit(2)

	return c.BROKER_ADDRESS



def open_map(map_path):
	c.logging.info("Opening map")
	tree = ET.parse(map_path)
	root = tree.getroot()
	return root
