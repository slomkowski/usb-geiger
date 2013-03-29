# -*- encoding: utf-8 -*-
'''
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
'''

import dummy
import ConfigParser
import time

class MySQLUpdaterException(dummy.UpdaterException):
	pass

class MySQLUpdater(dummy.DummyUpdater):
	"""Inserts data to MySQL table given. The table has to have columns named 'cpm', 'radiation' and 'time'. Autocommit
	mode is enabled.
	"""

	_dbName = None
	_dbUser = None
	_dbPassword = None
	_dbHost = None
	_db = None
	_tableName = None

	def __init__(self, configuration):
		"""Reads configuration from the file and starts the connection with the database. The connection
		is held during the whole program runtime.
		"""
		confFileSection = 'mysql'
		try:
			self._enabled = configuration.getboolean(confFileSection, 'enabled')
		except Exception:
			pass
		if self._enabled is False:
			return
		try:
			self._dbName = configuration.get(confFileSection, 'db_name')
			self._dbUser = configuration.get(confFileSection, 'user')
			self._dbPassword = configuration.get(confFileSection, 'password')
			self._dbHost = configuration.get(confFileSection, 'host')
			self._tableName = configuration.get(confFileSection, 'table_name')
		except ConfigParser.Error as e:
			self._enabled = False
			raise MySQLUpdaterException(str(e) + ". data is incomplete.")

		# import is  here to don't throw exceptions about missing MySQLdb odules if they're not used
		import MySQLdb

		try:
			self._db = MySQLdb.connect(host = self._dbHost, user = self._dbUser,
				passwd = self._dbPassword, db = self._dbName)
			self._db.autocommit(True)
		except MySQLdb.Error as e:
			self._enabled = False
			raise MySQLUpdaterException(str(e) + ". Connection failed.")

	def close(self):
		"Disconnects the database."
		self._db.close()

	def update(self, timestamp, radiation, cpm):
		"""Inserts new row to the database table. Both radiation and CPM have to be provided.
		"""
		import MySQLdb
		try:
			cursor = self._db.cursor()
			strTime = time.strftime('%Y-%m-%d %H:%M:%S', timestamp)
			cursor.execute("insert into " + self._tableName + "(radiation, cpm, time) values (%s, %s, %s)",
				(float(radiation), float(cpm), strTime))
			cursor.close()
		except MySQLdb.Error as e:
			raise MySQLUpdaterException("Could not insert new row to the table: " + str(e))
