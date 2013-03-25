# -*- encoding: utf8 -*-

import json
import httplib

class PachubeException(Exception):
	pass

class PachubeUpdater(object):
	_feedId = '120299'
	_CPMID = 'CPM'
	_RadiationID = 'Radiation'
	_apiKey = '_your_api_key'
	_version = '1.0.0'

	def __init__(self, configuration):
		pass

	def update(self, radiation = None, cpm = None):
		"Sends data to the server. Both parameters are optional."
		# construct message structure
		dataPoints = []
		if cpm is not None:
			dataPoints.append({'id': self._CPMID, 'current_value':cpm})
		if radiation is not None:
			dataPoints.append({'id': self._RadiationID, 'current_value' : radiation})

		if len(dataPoints) == 0:  # nothing to send
			return

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
