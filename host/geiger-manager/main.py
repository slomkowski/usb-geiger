#!/usr/bin/python2
# -*- encoding: utf-8 -*-
'''
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
'''

import argparse
import ConfigParser
import usbcomm
import sys
import os

__version__ = '0.1'
__author__ = 'Michał Słomkowski'
__copyright__ = 'GNU GPL v.3.0'

# default config file name
CONFIG_FILE_NAME = 'configuration.ini'
# directories with configuration file
CONFIG_PATH = [".", os.path.dirname(__file__), os.path.expanduser("~/.geiger"), "/etc/geiger"]

CONFIG_PATH = [os.path.realpath(os.path.join(directory, CONFIG_FILE_NAME)) for directory in CONFIG_PATH]

# parse command-line arguments
description = "Geiger manager v. " + __version__ + ', ' + __author__
description += """. This program provides a complex interface to USB Geiger device
including graphical user interface and monitor tools for pushing results to predefined MySQL table and cosm.com service. 
It needs configuration file to run, by default '""" + CONFIG_FILE_NAME + """'. It uses pyusb library."""

parser = argparse.ArgumentParser(description = description)
parser.add_argument("-c", "--config", nargs = 1, help = "reads given configuration file")
parser.add_argument("-v", "--verbose", action = 'store_true', help = "shows additional information")
group = parser.add_mutually_exclusive_group()
group.add_argument("-g", "--gui", action = 'store_true', help = "starts GUI window. Enabled by default")
group.add_argument("-m", "--monitor", action = 'store_true', help = "starts program in monitor mode")
group.add_argument("-s", "--status", action = 'store_true', help = "reads data from Geiger device and leaves")

args = parser.parse_args()

if args.verbose:
	print("Geiger manager v. " + __version__ + ', ' + __author__)

if args.config:
	CONFIG_PATH = []
	CONFIG_PATH.append(args.config[0])
	if args.verbose:
		print("Using configuration file '%s'" % args.config[0])

# load configuration file
conf = ConfigParser.SafeConfigParser()

for filePath in CONFIG_PATH:
	try:
		conf.readfp(open(filePath))
		configurationLoaded = True
		if args.verbose:
			print("Configuration file loaded from: " + filePath)
		break
	except IOError:
		configurationLoaded = False

if not configurationLoaded:
	sys.stderr.write("Error at loading configuration file.\n")
	sys.exit(1)

# establish USB connection
try:
	if args.verbose:
		print("Initializing Geiger device...")
	comm = usbcomm.Connector(conf)
except usbcomm.CommException as exp:
	sys.stderr.write("Error at initializing USB device: " + str(exp))
	sys.exit(1)

# display values from Geiger device and leave
if args.status:
	print(comm)
	sys.exit()

# launch GUI
if args.gui:
	import gui.gui
	if args.verbose:
		print("Launching GUI...")
	gui = gui.gui.GUIInterface(configuration = conf, usbcomm = usbcomm)
	gui.start()
	sys.exit()

# start monitor mode
if args.monitor:
	import monitor
	monitor = monitor.Monitor(configuration = conf, usbcomm = comm, verbose = args.verbose)
	monitor.start()
