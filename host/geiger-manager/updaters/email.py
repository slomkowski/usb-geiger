# -*- encoding: utf-8 -*-
"""
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
"""

import configparser
import smtplib
import time

import updaters

IDENTIFIER = 'SMTP e-mail notification'


class EmailNotificationException(updaters.UpdaterException):
    pass


class EmailNotificationUpdater(updaters.BaseUpdater):
    """Sends the e-mail notifications to the addresses on the list if the radiation or CPM level exceeds the given
    limit. You have to configure local SMTP server or use external one to use this module. """

    def __init__(self, configuration):
        """Reads configuration and sets up everything."""
        super().__init__(configuration)
        conf_file_section = 'email'
        try:
            self._enabled = configuration.getboolean(conf_file_section, 'enabled')
        except Exception:
            pass
        if self._enabled is False:
            return

        try:
            self._date_format = configuration.get(conf_file_section, 'date_format')
            self._time_format = configuration.get(conf_file_section, 'time_format')

            self._address_list = configuration.get(conf_file_section, 'addresses').split(';')
            self._address_list = map(lambda x: x.strip(), self._address_list)

            self._message_subject = configuration.get(conf_file_section, 'message_subject')
            self._messageContent = configuration.get(conf_file_section, 'message_content')

            self._smtp_server = configuration.get(conf_file_section, 'smtp_server')
            self._smtp_port = int(configuration.get(conf_file_section, 'smtp_port'))
            self._smtp_user = configuration.get(conf_file_section, 'smtp_user')
            self._smtp_password = configuration.get(conf_file_section, 'smtp_password')
            self._smtp_sender_email = configuration.get(conf_file_section, 'smtp_sender_email')

            self._threshold = configuration.get(conf_file_section, 'radiation_threshold')

        except configparser.Error as e:
            self._enabled = False
            raise EmailNotificationException("could not load all needed settings from the config file: " + str(e))

    def _fill_fields(self, tmpl, timestamp, radiation, cpm):
        timestamp = self.local_time(timestamp)
        curr_date = time.strftime(self._date_format, timestamp)
        curr_time = time.strftime(self._time_format, timestamp)

        replaces = {'$date$': curr_date, '$time$': curr_time, '$cpm$': cpm,
                    '$radiation$': radiation, '$threshold$': self._threshold, '\\n': '\n'}

        for old in replaces:
            tmpl = tmpl.replace(old, str(replaces[old]))

        return tmpl

    def update(self, timestamp, radiation=None, cpm=None):
        """If the radiation level exceeds the defined threshold, e-mails to all defined receivers are send."""

        if radiation < float(self._threshold):
            return

        subject = self._fill_fields(self._message_subject, timestamp, radiation, cpm)
        content = self._fill_fields(self._messageContent, timestamp, radiation, cpm)

        try:
            with smtplib.SMTP(self._smtp_server, self._smtp_port) as smtp_server:
                smtp_server.ehlo()
                smtp_server.starttls()
                smtp_server.ehlo()
                smtp_server.login(self._smtp_user, self._smtp_password)

                for address in self._address_list:
                    header = 'To:' + address + '\n' + 'From: ' + self._smtp_sender_email + '\n' + 'Subject:' + subject + '\n\n'
                    smtp_server.sendmail(self._smtp_sender_email, address, header + content)

        except Exception as e:
            raise EmailNotificationException("Failed to send notification e-mail: " + str(e))
