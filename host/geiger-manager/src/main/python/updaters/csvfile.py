# -*- encoding: utf-8 -*-
"""
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
"""

import configparser
import csv
import time

import updaters


class CsvFileException(updaters.UpdaterException):
    pass


class CsvFileUpdater(updaters.BaseUpdater):
    """Writes the CPM and radiation data to CSV file. Each row contains information: date, time, radiation in uSv/h
    and CPM (counts per minute) value. """

    conf_file_section = 'csvfile'
    full_name = "CSV file"

    def __init__(self, configuration: configparser.ConfigParser):
        """Reads configuration and opens the file to read."""
        super().__init__(configuration)
        try:
            self._enabled = configuration.getboolean(self.conf_file_section, 'enabled')
        except Exception:
            pass

        if self._enabled is False:
            return

        try:
            self._file_name = configuration.get(self.conf_file_section, 'file_name')
            self._dateFormat = configuration.get(self.conf_file_section, 'date_format')
            self._timeFormat = configuration.get(self.conf_file_section, 'time_format')
            self._decimalSep = configuration.get(self.conf_file_section, 'decimal_separator', fallback='.')
            self._delimiter = configuration.get(self.conf_file_section, 'delimiter')
        except configparser.Error as e:
            self._enabled = False
            raise CsvFileException("could not load all needed settings from the config file: " + str(e))

        try:
            with open(self._file_name, 'a', newline='') as fp:
                # write header
                if fp.tell() == 0:
                    print("Adding header to CSV file.")
                    wr = csv.writer(fp, delimiter=self._delimiter)
                    wr.writerow(("Date:",
                                 "Time:",
                                 "Radiation [uSv/h]:",
                                 "CPM:"))
        except IOError as e:
            self._enabled = False
            raise CsvFileException("could not open log file to write: " + str(e))

    def update(self, timestamp, radiation=None, cpm=None):
        timestamp = self.local_time(timestamp)
        curr_date = time.strftime(self._dateFormat, timestamp)
        curr_time = time.strftime(self._timeFormat, timestamp)
        try:
            with open(self._file_name, 'a', newline='') as fp:
                wr = csv.writer(fp, delimiter=self._delimiter)
                wr.writerow((curr_date,
                             curr_time,
                             str(radiation).replace('.', self._decimalSep),
                             str(cpm).replace('.', self._decimalSep)))
        except IOError as e:
            raise CsvFileException("could not write row to the CSV file: " + str(e))
