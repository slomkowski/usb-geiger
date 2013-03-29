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
		except Exception as e:
			sys.stderr.write("Measuring interval wrong or not provided: " + str(e) + "\n")
			sys.exit(1)

		if verbose:
			print("Setting programmed voltage and interval to %d." % self._interval)
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
		"""Enables cyclic monitoring. The firs measurement cycle has the 1.5 length of the given interval
		in order to collect data by the device.
		"""
		self._timer = threading.Timer(self._interval / 2, self._update)
		self._timer.start()

	def _update(self):
		self._timer = threading.Timer(self._interval, self._update)
		if self._firstCycle:
			self._firstCycle = False
			if self._verbose:
				print("Skipping first cycle.")
			self._timer.start()
			return

		radiation = self._usbcomm.getRadiation()
		cpm = self._usbcomm.getCPM()

		if self._verbose:
			currTime = time.strftime("%H:%M:%S", time.gmtime())
			print("%s Pushing data: %f CPM, %f uSv/h" % (currTime, cpm, radiation))

		for updater in self._updatersList:
			updater.update(radiation = radiation, cpm = cpm)

		self._timer.start()
