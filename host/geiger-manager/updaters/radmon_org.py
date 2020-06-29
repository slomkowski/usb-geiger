# -*- encoding: utf-8 -*-
"""
 * USB Geiger counter manager
 * 2020 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
"""

import configparser
import http.client
import time
import urllib.parse

import updaters

IDENTIFIER = 'radmon.org updater'


class RadmonOrgException(updaters.UpdaterException):
    pass


class RadmonOrgUpdater(updaters.BaseUpdater):
    def __init__(self, configuration):
        super().__init__(configuration)
        conf_file_section = 'radmon.org'
        try:
            self._enabled = configuration.getboolean(conf_file_section, 'enabled')
        except configparser.Error:
            pass
        if self._enabled is False:
            return
        try:
            self._user = configuration.get(conf_file_section, 'user')
            self._password = configuration.get(conf_file_section, 'password')

            latitude = configuration.getfloat(conf_file_section, 'latitude', fallback=None)
            longitude = configuration.getfloat(conf_file_section, 'longitude', fallback=None)

            if latitude is not None and longitude is not None:
                if not -90.0 <= latitude <= 90.0:
                    raise RadmonOrgException("latitude value %f is invalid" % latitude)
                if not -180.0 <= latitude <= 180.0:
                    raise RadmonOrgException("longitude value %f is invalid" % longitude)
                self._position = (latitude, longitude)
            elif latitude is None and longitude is None:
                self._position = None
            else:
                raise RadmonOrgException("both latitude and longitude has to be provided or nothing at all")

        except configparser.Error as e:
            self._enabled = False
            raise RadmonOrgException(str(e) + ". data is incomplete.")

    def update(self, timestamp, radiation=None, cpm=None):
        """Sends data to radmon.org. Radmon.org supports only CPM, so cpm argument has to be provided."""
        if not self._enabled:
            return

        if cpm is None:
            raise RadmonOrgException("this updater needs provision of CPM value")

        # radmon.org accepts ISO local time format, but in fact, this is UTC
        time_str = time.strftime("%Y-%m-%dT%H:%M:%S", timestamp)

        parameters = {
            'user': self._user,
            'password': self._password,
            'value': int(cpm),
            'unit': 'CPM',
            'datetime': time_str
        }
        if self._position:
            (latitude, longitude) = self._position
            parameters.update({
                'latitude': latitude,
                'longitude': longitude,
                'function': 'submitwithlatlng'
            })
        else:
            parameters['function'] = 'submit'

        try:
            conn = http.client.HTTPConnection("radmon.org", timeout=10)
            conn.request("GET", "/radmon.php?%s" % urllib.parse.urlencode(parameters))
            res = conn.getresponse()
            if res.status != 200:
                raise RadmonOrgException("invalid server response: %d, %s." % (res.status, res.reason))
            resp_text = res.read().decode("utf-8")
            if "OK<br>" != resp_text.strip():
                raise RadmonOrgException("invalid server response: %s" % resp_text)
        except Exception as e:
            raise RadmonOrgException("error at sending values to radmon.org: " + str(e))
