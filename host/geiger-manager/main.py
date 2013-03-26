#!/usr/bin/python2
# -*- encoding: utf8 -*-

import ConfigParser
import usbcomm
import sys

CONFIG_FILE_NAME = 'configuration.ini'

cosmEnabled = True
mysqlEnabled = True

conf = ConfigParser.SafeConfigParser()
try:
	conf.readfp(open(CONFIG_FILE_NAME))
except IOError as exp:
	sys.stderr.write("Error at loading configuration file: " + exp.strerror)
	sys.exit(1)

comm = usbcomm.Connector(conf)

print(comm)

updatersList = []

if cosmEnabled:
	import updaters.cosm
	c = updaters.cosm.PachubeUpdater(conf)
	updatersList.append(c)

if mysqlEnabled:
	import updaters.mysql
	mysql = updaters.mysql.MySQLUpdater(conf)
	updatersList.append(mysql)

for u in updatersList:
	u.update(radiation = comm.getRadiation(), cpm = comm.getCPM())



