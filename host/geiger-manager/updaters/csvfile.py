# -*- encoding: utf-8 -*-
'''
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
'''

import dummy
import time
import csv
import ConfigParser

class CsvFileException(dummy.UpdaterException):
	pass

class CsvFileUpdater(dummy.DummyUpdater):
	"""Writes the CPM and radiation data to CSV file. Each row contains information: date, time, radiation in uSV/h
	and CPM (counts per minute) value.
	"""
	_csv = None
	_fileHandle = None

	_dateFormat = None
	_timeFormat = None
	_decimalSep = '.'

	def __init__(self, configuration):
		"""Reads configuration and opens the file to read."""
		confFileSection = 'csvfile'
		try:
			self._enabled = configuration.getboolean(confFileSection, 'enabled')
		except Exception:
			pass
		if self._enabled is False:
			return
		try:
			fileName = configuration.get(confFileSection, 'file_name')
			self._dateFormat = configuration.get(confFileSection, 'date_format')
			self._timeFormat = configuration.get(confFileSection, 'time_format')
			self._decimalSep = configuration.get(confFileSection, 'decimal_separator')
			delimiter = configuration.get(confFileSection, 'delimiter')
		except ConfigParser.Error as e:
			self._enabled = False
			raise CsvFileException("could not load all needed settings from the config file: " + str(e))

		try:
			self._fileHandle = open(fileName, 'ab')
			self._csv = csv.writer(self._fileHandle, delimiter = delimiter)

			# write header
			if self._fileHandle.tell() == 0:
				print("Adding header to CSV file.")
				self._csv.writerow(("Date:", "Time:", "Radiation [uSv/h]:", "CPM:"))
		except IOError as e:
			self._enabled = False
			raise CsvFileException("could not open log file to write: " + str(e))

	def close(self):
		"Closes the file."
		self._enabled = False
		self._fileHandle.close()

	def update(self, radiation, cpm):
		times = time.gmtime()
		currDate = time.strftime(self._dateFormat, times)
		currTime = time.strftime(self._timeFormat, times)
		try:
			self._csv.writerow((currDate, currTime, str(radiation).replace('.', self._decimalSep),
					str(cpm).replace('.', self._decimalSep)))
			self._fileHandle.flush()
		except IOError as e:
			raise CsvFileException("could not write row to the CSV file: " + str(e))
