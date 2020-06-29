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

IDENTIFIER = 'CSV file'


class CsvFileException(updaters.UpdaterException):
    pass


class CsvFileUpdater(updaters.BaseUpdater):
    """Writes the CPM and radiation data to CSV file. Each row contains information: date, time, radiation in uSv/h
    and CPM (counts per minute) value. """

    def __init__(self, configuration: configparser.ConfigParser):
        """Reads configuration and opens the file to read."""
        super().__init__(configuration)
        conf_file_section = 'csvfile'
        try:
            self._enabled = configuration.getboolean(conf_file_section, 'enabled')
        except Exception:
            pass
        if self._enabled is False:
            return

        try:
            file_name = configuration.get(conf_file_section, 'file_name')
            self._dateFormat = configuration.get(conf_file_section, 'date_format')
            self._timeFormat = configuration.get(conf_file_section, 'time_format')
            self._decimalSep = configuration.get(conf_file_section, 'decimal_separator', fallback='.')
            delimiter = configuration.get(conf_file_section, 'delimiter')
        except configparser.Error as e:
            self._enabled = False
            raise CsvFileException("could not load all needed settings from the config file: " + str(e))

        try:
            self._fileHandle = open(file_name, 'ab')
            self._csv = csv.writer(self._fileHandle, delimiter=delimiter)

            # write header
            if self._fileHandle.tell() == 0:
                print("Adding header to CSV file.")
                self._csv.writerow(("Date:", "Time:", "Radiation [uSv/h]:", "CPM:"))
        except IOError as e:
            self._enabled = False
            raise CsvFileException("could not open log file to write: " + str(e))

    def close(self):
        """Closes the file."""
        self._enabled = False
        self._fileHandle.close()

    def update(self, timestamp, radiation=None, cpm=None):
        timestamp = self.local_time(timestamp)
        curr_date = time.strftime(self._dateFormat, timestamp)
        curr_time = time.strftime(self._timeFormat, timestamp)
        try:
            self._csv.writerow((curr_date, curr_time, str(radiation).replace('.', self._decimalSep),
                                str(cpm).replace('.', self._decimalSep)))
            self._fileHandle.flush()
        except IOError as e:
            raise CsvFileException("could not write row to the CSV file: " + str(e))
