# -*- encoding: utf8 -*-

from abc import ABCMeta

class UpdaterException(Exception):
	pass

class DummyUpdater(object):
	"""This 'abstract' class provides and interface for all updater modules."""

	__metaclass__ = ABCMeta
	_enabled = False

	def __init__(self, configuration):
		pass

	def update(self, radiation = None, cpm = None):
		"""Sends data wherever they are sent. Both parameters are optional. Raises exception if no data
		was delivered
		"""
		raise NotImplementedError
