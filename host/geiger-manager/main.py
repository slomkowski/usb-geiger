#!/usr/bin/python2
# -*- encoding: utf8 -*-

import ConfigParser
import usbcomm
import sys
import cosm

CONFIG_FILE_NAME = 'configuration.ini'

cosmEnabled = True
mysqlEnabled = False

conf = ConfigParser.SafeConfigParser()
try:
	conf.readfp(open(CONFIG_FILE_NAME))
except IOError as exp:
	sys.stderr.write("Error at loading configuration file: " + exp.strerror)
	sys.exit(1)

comm = usbcomm.Connector(conf)

print(comm)

if cosmEnabled:
	cosm = cosm.PachubeUpdater(conf)
	cosm.update(comm.getRadiation(), comm.getCPM())
