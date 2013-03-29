# -*- encoding: utf-8 -*-
'''
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
'''

import sys
import threading
import time
import updaters.dummy
import importlib
import ConfigParser
import usbcomm

class Monitor(object):

	_interval = None
	_usbcomm = None
	_verbose = False
	_configuration = None

	_timer = None

	_updatersList = []

	_firstCycle = True

	def __init__(self, configuration, usbcomm, verbose):
		self._verbose = verbose
		self._usbcomm = usbcomm
		self._configuration = configuration
		confFileSection = 'monitor'
		try:
			self._interval = configuration.getint(confFileSection, 'interval')
		except ConfigParser.Error as e:
			sys.stderr.write("Measuring interval wrong or not provided: " + str(e) + "\n")
			sys.exit(1)

		if verbose:
			print("Setting programmed voltage and interval to %d seconds." % self._interval)
		usbcomm.setVoltageFromConfigFile()
		usbcomm.setInterval(self._interval)

		self._initialize("cosm.com", "cosm", "PachubeUpdater")
		self._initialize("MySQL", "mysql", "MySQLUpdater")
		self._initialize("CSV file", "csvfile", "CsvFileUpdater")


	def _initialize(self, name, importName, className):
		importlib.import_module("updaters." + importName, "updaters")
		try:
			u = getattr(sys.modules["updaters." + importName], className)(self._configuration)
			if u.isEnabled():
				self._updatersList.append(u)
				if self._verbose:
					print(name + " updater enabled.")
		except updaters.dummy.UpdaterException as e:
			sys.stderr.write("Error at initializing %s updater: %s. Disabling." % (name, str(e)))

	def start(self):
		"""Enables cyclic monitoring. The first measurement cycle has the 1.5 length of the given interval
		in order to collect data by the device.
		"""
		self._timer = threading.Timer(self._interval / 2, self._update)
		self._timer.setDaemon(True)
		self._timer.start()

	def stop(self):
		"""Stops measuring cycle and closes all updaters."""
		self._timer.cancel()

		if self._verbose:
			print("Stopping all updaters.")

		for updater in self._updatersList:
			updater.close()

	def _update(self):
		self._timer = threading.Timer(self._interval, self._update)
		self._timer.setDaemon(True)
		if self._firstCycle:
			self._firstCycle = False
			if self._verbose:
				print("Skipping first cycle.")
			self._timer.start()
			return

		timestamp = time.gmtime()

		try:
			radiation = self._usbcomm.getRadiation()
			cpm = self._usbcomm.getCPM()
		except usbcomm.CommException as e:
			sys.stderr.write("USB device error: " + str(e) + ". Skipping cycle.")
			self._timer.start()
			return

		if self._verbose:
			currTime = time.strftime("%H:%M:%S", timestamp)
			print("[%s] pushing data: %f CPM, %f uSv/h" % (currTime, cpm, radiation))

		for updater in self._updatersList:
			updater.update(radiation = radiation, cpm = cpm, timestamp = timestamp)

		self._timer.start()
