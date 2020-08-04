# -*- encoding: utf-8 -*-
"""
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
"""

import abc
import calendar
import time


class UpdaterException(Exception):
    pass


class BaseUpdater(abc.ABC):
    """This 'abstract' class provides and interface for all updater modules."""

    _enabled = False

    def __init__(self, configuration):
        pass

    def is_enabled(self):
        """Returns status basing on configuration file entry."""
        return self._enabled

    def close(self):
        """Frees the resources."""
        self._enabled = False

    _timeDiffMeasured = None

    def local_time(self, utc_time):
        """Takes time_struct in UTC and returns time_struct in local time."""

        # check the difference only once
        if self._timeDiffMeasured is None:
            local = calendar.timegm(time.localtime())
            utc = calendar.timegm(time.gmtime())

            self._timeDiffMeasured = local - utc

        return time.gmtime(calendar.timegm(utc_time) + self._timeDiffMeasured)

    @abc.abstractmethod
    def update(self, timestamp: time.struct_time, radiation: float = None, cpm: float = None):
        """Sends data wherever they are sent. Both parameters are optional. Raises exception if no data was
        delivered. """
        raise NotImplementedError

    @property
    def full_name(self):
        raise NotImplementedError
