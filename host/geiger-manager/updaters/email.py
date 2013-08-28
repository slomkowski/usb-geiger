# -*- encoding: utf-8 -*-
'''
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
'''

import dummy
import time
import ConfigParser
import smtplib

IDENTIFICATOR = 'SMTP e-mail notification'

class EmailNotificationException(dummy.UpdaterException):
	pass

class EmailNotificationUpdater(dummy.DummyUpdater):
	"""Sends the e-mail notifications to the addresses on the list if the radiation or CPM level exceeds
	the given limit. You have to configure local SMTP server or use external one to use this module.
	"""

	_dateFormat = None
	_timeFormat = None

	_addressList = None
	_messageSubject = None
	_messageContent = None

	_smtp_server = None
	_smtp_port = None
	_smtp_user = None
	_smtp_password = None
	_smtp_sender_email = None

	_threshold = None

	def __init__(self, configuration):
		"""Reads configuration and sets up everything."""
		confFileSection = 'email'
		try:
			self._enabled = configuration.getboolean(confFileSection, 'enabled')
		except Exception:
			pass
		if self._enabled is False:
			return

		try:
			self._dateFormat = configuration.get(confFileSection, 'date_format')
			self._timeFormat = configuration.get(confFileSection, 'time_format')

			self._addressList = configuration.get(confFileSection, 'addresses').split(';')
			self._addressList = map(lambda x: x.strip(), self._addressList)

			self._messageSubject = configuration.get(confFileSection, 'message_subject')
			self._messageContent = configuration.get(confFileSection, 'message_content')

			self._smtp_server = configuration.get(confFileSection, 'smtp_server')
			self._smtp_port = int(configuration.get(confFileSection, 'smtp_port'))
			self._smtp_user = configuration.get(confFileSection, 'smtp_user')
			self._smtp_password = configuration.get(confFileSection, 'smtp_password')
			self._smtp_sender_email = configuration.get(confFileSection, 'smtp_sender_email')

			self._threshold = configuration.get(confFileSection, 'radiation_threshold')

		except ConfigParser.Error as e:
			self._enabled = False
			raise EmailNotificationException("could not load all needed settings from the config file: " + str(e))

	def _fillFields(self, tmpl, timestamp, radiation, cpm):
		timestamp = self.localTime(timestamp)
		currDate = time.strftime(self._dateFormat, timestamp)
		currTime = time.strftime(self._timeFormat, timestamp)

		replaces = {'$date$' : currDate, '$time$' : currTime, '$cpm$' : cpm,
			'$radiation$' : radiation, '$threshold$' : self._threshold, '\\n' : '\n' }

		for old in replaces:
			tmpl = tmpl.replace(old, str(replaces[old]))

		return tmpl



	def update(self, timestamp, radiation, cpm):
		"""If the radiation level exceeds the defined threshold, e-mails to all defined receivers are send.
		"""

		if radiation < float(self._threshold):
			return

		subject = self._fillFields(self._messageSubject, timestamp, radiation, cpm)
		content = self._fillFields(self._messageContent, timestamp, radiation, cpm)

		try:
			smtpserver = smtplib.SMTP(self._smtp_server, self._smtp_port)
			smtpserver.ehlo()
			smtpserver.starttls()
			smtpserver.ehlo
			smtpserver.login(self._smtp_user, self._smtp_password)

			for address in self._addressList:
				header = 'To:' + address + '\n' + 'From: ' + self._smtp_sender_email + '\n' + 'Subject:' + subject + '\n\n'
				smtpserver.sendmail(self._smtp_sender_email, address, header + content)

			smtpserver.close()
		except Exception as e:
			raise EmailNotificationException("Failed to send notification e-mail: " + str(e))
