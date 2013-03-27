# -*- encoding: utf8 -*-
'''
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
'''

from abc import ABCMeta

class UpdaterException(Exception):
	pass

class DummyUpdater(object):
	"""This 'abstract' class provides and interface for all updater modules."""

	__metaclass__ = ABCMeta
	_enabled = False

	def __init__(self, configuration):
		pass

	def isEnabled(self):
		"Returns status basing on configuration file entry."
		return self._enabled

	def update(self, radiation = None, cpm = None):
		"""Sends data wherever they are sent. Both parameters are optional. Raises exception if no data
		was delivered
		"""
		raise NotImplementedError
