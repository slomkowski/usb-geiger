# -*- encoding: utf-8 -*-
'''
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
'''

import sys
import os
import threading
import thread
import time
import updaters.dummy
import importlib
import ConfigParser
import usbcomm
import logging

class Monitor(object):

	_interval = None
	_usbcomm = None
	_log = False
	_configuration = None

	_timer = None

	_updatersList = []

	def __init__(self, configuration, usbcomm):
		self._log = logging.getLogger("geiger.monitor")
		self._usbcomm = usbcomm
		self._configuration = configuration
		confFileSection = 'monitor'
		try:
			self._interval = configuration.getint(confFileSection, 'interval')
		except ConfigParser.Error as e:
			self._log.critical("Measuring interval wrong or not provided: %s.", str(e))
			sys.exit(1)

		self._log.info("Setting programmed voltage and interval to %d seconds.", self._interval)

		usbcomm.setVoltageFromConfigFile()
		usbcomm.setInterval(self._interval)

		# initialize all updater modules in the directory
		for files in os.listdir(os.path.join(os.path.dirname(__file__), "updaters")):
			if files.endswith(".py"):
				self._initializeUpdater(files[:-3])


	def _initializeUpdater(self, importName):
		importlib.import_module("updaters." + importName, "updaters")

		module = sys.modules["updaters." + importName]

		for elem in getattr(module, '__dict__'):
			if elem.endswith('Updater'):
				className = elem
		try:
			name = getattr(module, 'IDENTIFICATOR')
		except:
			return
		try:
			u = getattr(module, className)(self._configuration)
			if u.isEnabled():
				self._updatersList.append(u)
				self._log.info("%s updater enabled.", name)
		except updaters.dummy.UpdaterException as e:
			self._log.error("Error at initializing %s updater: %s. Disabling.", name, str(e))

	def start(self):
		"""Enables cyclic monitoring. The first measurement cycle has the 1.5 length of the given interval
		in order to collect data by the device.
		"""
		self._timer = threading.Timer(1.5 * self._interval, self._update)
		self._timer.setDaemon(True)
		self._timer.start()

	def stop(self):
		"""Stops measuring cycle and closes all updaters."""
		self._timer.cancel()

		self._log.info("Stopping all updaters.")

		for updater in self._updatersList:
			if updater.isEnabled():
				updater.close()

	def _update(self):
		"""This method is called by the internal timer every 'interval' time to gather measurements
		and send them to specified updaters. The first cycle has 1.5*interval length to give the
		Geiger device time to collect counts. Then, update takes place in the middle of the next
		measuring cycle.
		"""

		self._timer = threading.Timer(self._interval, self._update)
		self._timer.setDaemon(True)
		# start new cycle here to prevent shifting next update time stamp
		self._timer.start()

		timestamp = time.gmtime()

		try:
			cpm, radiation = self._usbcomm.getCPMandRadiation()
		except usbcomm.CommException as e:
			self._log.error("USB device error: %s. Forcing device reset and wait of 1.5 cycle length.", str(e))
			self._log.info("Resetting device.")
			try:
				self._usbcomm.resetConnection()
				self._log.info("Setting programmed voltage and interval to %d seconds.", self._interval)
				self._usbcomm.setVoltageFromConfigFile()
				self._usbcomm.setInterval(self._interval)
			except usbcomm.CommException as e:
				self._log.critical("Error at reinitializing device: %s", str(e))
				self.stop()
				# close entire application
				thread.interrupt_main()

			self._timer.cancel()
			self._timer = threading.Timer(1.5 * self._interval, self._update)
			self._timer.setDaemon(True)
			self._timer.start()
			return

		self._log.info("pushing data: %f CPM, %f uSv/h", cpm, radiation)

		for updater in self._updatersList:
			try:
				updater.update(radiation = radiation, cpm = cpm, timestamp = timestamp)
			except updaters.dummy.UpdaterException as exp:
				self._log.error("Updater error: %s", str(exp))
