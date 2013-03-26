# -*- encoding: utf8 -*-
import MySQLdb
import datetime
import dummy

class MySQLUpdaterException(dummy.UpdaterException):
	pass

class MySQLUpdater(dummy.DummyUpdater):

	_dbName = None
	_dbUser = None
	_dbPassword = None
	_dbHost = None
	_db = None
	_tableName = None

	def __init__(self, configuration):
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
		except Exception as e:
			self._enabled = False
			raise MySQLUpdaterException(str(e) + ". data is incomplete. Disabling.")

		try:
			self._db = MySQLdb.connect(host = self._dbHost, user = self._dbUser,
				passwd = self._dbPassword, db = self._dbName)
			self._db.autocommit(True)
		except MySQLdb.Error as e:
			self._enabled = False
			raise MySQLUpdaterException(str(e) + ". Connection failed.")

	def update(self, radiation, cpm):
		"""Inserts new row to the database table. Both radiation and CPM have to be provided.
		"""
		try:
			cursor = self._db.cursor()
			cursor.execute("insert into " + self._tableName + "(radiation, cpm) values (%s, %s)",
				(float(radiation), float(cpm)))
			cursor.close()
		except MySQLdb.Error as e:
			raise MySQLUpdaterException("Could not insert new row to the table: " + str(e))
