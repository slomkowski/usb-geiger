# -*- encoding: utf-8 -*-
"""
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
"""

import configparser
import logging
import threading
import time
from collections import Iterator

import updaters
import usbcomm
from updaters.csvfile import CsvFileUpdater
from updaters.email import EmailNotificationUpdater
from updaters.mysql import MySQLUpdater
from updaters.radmon_org import RadmonOrgUpdater


def find_updaters(configuration: configparser.ConfigParser) -> [updaters.BaseUpdater]:
    # todo replace with dynamic module walking
    return list(filter(lambda u: u.is_enabled(),
                  [EmailNotificationUpdater(configuration),
                   CsvFileUpdater(configuration),
                   MySQLUpdater(configuration),
                   RadmonOrgUpdater(configuration)]))


class Monitor(object):
    _conf_file_section = "monitor"
    _log = logging.getLogger("geiger.monitor")

    error: Exception = None

    def __init__(self,
                 configuration: configparser.ConfigParser,
                 comm: usbcomm.Connector,
                 updaters_list: [updaters.BaseUpdater]):
        self._usbcomm = comm
        self._updaters = updaters_list

        if not self._updaters:
            raise Exception("At least one updater has to be enabled.")

        try:
            self._interval = configuration.getint(self._conf_file_section, 'interval')
        except configparser.Error as e:
            raise Exception("Measuring interval wrong or not provided:", e)

        self._log.info("Setting programmed voltage and interval to %d seconds.", self._interval)

        self._usbcomm.set_voltage_from_config_file()
        self._usbcomm.set_interval(self._interval)

        self._timer = threading.Timer(1.5 * self._interval, self._perform_update_every_tick)
        self._timer.setDaemon(True)
        self._timer.start()

    def stop(self):
        """Stops measuring cycle and closes all updaters."""
        self._timer.cancel()

        self._log.info("Stopping all updaters.")

        for updater in self._updaters:
            if updater.is_enabled():
                updater.close()

    def _perform_update_every_tick(self):
        """This method is called by the internal timer every 'interval' time to gather measurements and send them to
        specified updaters. The first cycle has 1.5*interval length to give the Geiger device time to collect counts.
        Then, update takes place in the middle of the next measuring cycle."""

        self._timer = threading.Timer(self._interval, self._perform_update_every_tick)
        self._timer.setDaemon(True)
        # start new cycle here to prevent shifting next update time stamp
        self._timer.start()

        timestamp = time.gmtime()

        try:
            cpm, radiation = self._usbcomm.get_cpm_and_radiation()
        except usbcomm.CommException as e:
            self._log.error("USB device error: %s. Forcing device reset and wait of 1.5 cycle length.", str(e))
            self._log.info("Resetting device.")
            try:
                self._usbcomm.reset_connection()
                self._log.info("Setting programmed voltage and interval to %d seconds.", self._interval)
                self._usbcomm.set_voltage_from_config_file()
                self._usbcomm.set_interval(self._interval)
            except usbcomm.CommException as e:
                self._log.critical("Error at reinitializing device: %s", str(e))
                self.stop()
                self.error = e
                return

            self._timer.cancel()
            self._timer = threading.Timer(1.5 * self._interval, self._perform_update_every_tick)
            self._timer.setDaemon(True)
            self._timer.start()
            return

        self._log.info("Pushing data: %f CPM, %f uSv/h", cpm, radiation)

        for updater in self._updaters:
            try:
                updater.update(timestamp=timestamp, radiation=radiation, cpm=cpm)
            except updaters.UpdaterException as exp:
                self._log.error("Updater error: %s", str(exp))
