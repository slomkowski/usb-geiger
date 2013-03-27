# -*- encoding: utf8 -*-
'''
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
'''

import json
import httplib
import dummy

class PachubeException(dummy.UpdaterException):
	pass

class PachubeUpdater(dummy.DummyUpdater):
	_feedId = None
	_CPMID = None
	_RadiationID = None
	_apiKey = None
	_version = '1.0.0'

	def __init__(self, configuration):
		confFileSection = 'cosm.com'
		try:
			self._enabled = configuration.getboolean(confFileSection, 'enabled')
		except Exception:
			pass
		if self._enabled is False:
			return
		try:
			self._feedId = configuration.get(confFileSection, 'feed_id')
			self._RadiationID = configuration.get(confFileSection, 'radiation_id')
			self._CPMID = configuration.get(confFileSection, 'cpm_id')
			self._apiKey = configuration.get(confFileSection, 'api_key')
		except Exception as e:
			self._enabled = False
			raise PachubeException(str(e) + ". data is incomplete. Disabling.")


	def update(self, radiation = None, cpm = None):
		"""Sends data to the server. Both parameters are optional, but at least one should be specified.
		Warning! If radiation_id or cpm_id are specified in the wrong way, there's no information about that.
		Only bad API key or feed ID are beeing checked by the server.
		"""
		if not self._enabled:
			return
		# construct message structure
		dataPoints = []
		if cpm is not None:
			dataPoints.append({'id': self._CPMID, 'current_value':cpm})
		if radiation is not None:
			dataPoints.append({'id': self._RadiationID, 'current_value' : radiation})

		if len(dataPoints) == 0:  # nothing to send
			raise PachubeException("no data to send")

		mesg = {}
		mesg['version'] = self._version
		mesg['id'] = self._feedId
		mesg['datastreams'] = dataPoints

		# send it
		headers = {"X-PachubeApiKey" : self._apiKey}
		try:
			conn = httplib.HTTPConnection('api.cosm.com')
			conn.request("PUT", '//v2/feeds/' + self._feedId, json.dumps(mesg), headers)
			if conn.getresponse().status != 200:
				raise Exception("bad response")
			conn.close()
		except Exception as e:
			conn.close()
			raise PachubeException("Error at sending values to cosm.com: " + str(e))
