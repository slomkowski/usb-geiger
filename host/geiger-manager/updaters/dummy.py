# -*- encoding: utf-8 -*-
'''
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
'''

import time
import calendar
import abc

class UpdaterException(Exception):
	pass

class DummyUpdater(object):
	"""This 'abstract' class provides and interface for all updater modules."""

	__metaclass__ = abc.ABCMeta
	_enabled = False

	def __init__(self, configuration):
		pass

	def isEnabled(self):
		"Returns status basing on configuration file entry."
		return self._enabled

	def close(self):
		"Frees the resources."
		self._enabled = False

	_timeDiffMeasured = None

	def localTime(self, utcTime):
		"Takes time_struct in UTC and returns time_struct in local time."

		# check the difference only once
		if self._timeDiffMeasured is None:
			local = calendar.timegm(time.localtime())
			utc = calendar.timegm(time.gmtime())

			self._timeDiffMeasured = local - utc

		return time.gmtime(calendar.timegm(utcTime) + self._timeDiffMeasured)

	def update(self, timestamp, radiation = None, cpm = None):
		"""Sends data wherever they are sent. Both parameters are optional. Raises exception if no data
		was delivered
		"""
		raise NotImplementedError
