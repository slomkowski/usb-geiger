# -*- encoding: utf-8 -*-
"""
 * USB Geiger counter manager
 * 2013, 2020 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
"""

import configparser
import time

import updaters


class MySQLUpdaterException(updaters.UpdaterException):
    pass


class MySQLUpdater(updaters.BaseUpdater):
    """Inserts data to MySQL table given. The table has to have columns named 'cpm', 'radiation' and 'time'. Connects
    the database each time. """

    conf_file_section = 'mysql'
    full_name = "MySQL"

    def __init__(self, configuration):
        """Reads configuration from the file and starts the connection with the database. The connection is held
        during the whole program runtime. """
        super().__init__(configuration)
        try:
            self._enabled = configuration.getboolean(self.conf_file_section, 'enabled')
        except Exception:
            pass
        if self._enabled is False:
            return
        try:
            self._dbName = configuration.get(self.conf_file_section, 'db_name')
            self._dbUser = configuration.get(self.conf_file_section, 'user')
            self._dbPassword = configuration.get(self.conf_file_section, 'password')
            self._dbHost = configuration.get(self.conf_file_section, 'host')
            self._tableName = configuration.get(self.conf_file_section, 'table_name')
        except configparser.Error as e:
            self._enabled = False
            raise MySQLUpdaterException(str(e) + ". data is incomplete.")

        # import is  here to don't throw exceptions about missing MySQLdb modules if they're not used
        import pymysql

        try:
            db = pymysql.connect(host=self._dbHost, user=self._dbUser,
                                 passwd=self._dbPassword, db=self._dbName)
            db.close()
        except pymysql.Error as e:
            self._enabled = False
            raise MySQLUpdaterException(str(e) + ". Connection failed.")

    def update(self, timestamp, radiation=None, cpm=None):
        """Inserts new row to the database table. Both radiation and CPM have to be provided."""
        import pymysql
        try:
            db = pymysql.connect(host=self._dbHost, user=self._dbUser,
                                 passwd=self._dbPassword, db=self._dbName)

            cursor = db.cursor()
            str_time = time.strftime('%Y-%m-%d %H:%M:%S', self.local_time(timestamp))
            cursor.execute("insert into " + self._tableName + "(radiation, cpm, time) values (%s, %s, %s)",
                           (float(radiation), float(cpm), str_time))
            cursor.close()
            db.commit()
            db.close()

        except pymysql.Error as e:
            raise MySQLUpdaterException("Could not insert new row to the table: " + str(e))
