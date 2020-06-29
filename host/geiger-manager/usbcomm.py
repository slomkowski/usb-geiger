# -*- encoding: utf-8 -*-
"""
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
"""

import configparser
import logging

import usb.core
import usb.util

# these values are provided with V-USB for shared use
VENDOR_ID = 0x16c0
DEVICE_ID = 0x05df

# these distinguish the Geiger counter from other devices with the same vendor and device IDs
VENDOR_NAME = "slomkowski.eu"
DEVICE_NAME = "USB Geiger"

# request numbers
GET_CPI = 10
SET_INTERVAL = 20
GET_INTERVAL = 21
SET_VOLTAGE = 30
GET_VOLTAGE = 31
ACKNOWLEDGE_UNCHECKED_COUNT = 40

# default values
TUBE_SENSITIVITY = 25.0
VOLTAGE_DIVIDER_UPPER_RESISTOR = 2000
VOLTAGE_DIVIDER_LOWER_RESISTOR = 4.7
TUBE_VOLTAGE = 390

# unmodifiable values
TIMER_TICKS_PER_SECOND = 100
MIN_VOLTAGE = 50
MAX_VOLTAGE = 450


class CommException(Exception):
    """This exception is thrown if an USB communication error with the Geiger device occurs."""
    pass


class RawConnector(object):
    """Low level class for Geiger device communication. It handles all libusb calls and supports all low level
    functions. Warning! Methods like getVoltage, getInterval don't return values in standard units like seconds or
    volts, but device internal representations. You should use this class wrapped by some class transforming them to
    standard units. """

    _device = None

    def __init__(self):
        """Initiates the class and opens the device. Warning! The constructor assumes that only one Geiger device is
        connected to the bus. Otherwise, it opens the first-found one. """
        self._open_device()

    def _open_device(self):
        for dev in usb.core.find(idVendor=VENDOR_ID, idProduct=DEVICE_ID, find_all=True):
            vendor_name = usb.util.get_string(dev, 256, dev.iManufacturer)
            device_name = usb.util.get_string(dev, 256, dev.iProduct)

            if vendor_name == VENDOR_NAME and device_name == DEVICE_NAME:
                self._device = dev
                break

        if self._device is None:
            raise CommException("Geiger device not found")

    def reset_connection(self):
        """Forces the device to reset and discovers it one more time."""
        try:
            self._device.reset()
            usb.util.dispose_resources(self._device)
        except usb.core.USBError:
            pass
        self._open_device()

    def _send_message(self, request, value):
        if value > 0xffff:
            raise CommException("device doesn't support values longer than two bytes")

        request_type = usb.util.build_request_type(usb.util.ENDPOINT_OUT, usb.util.CTRL_TYPE_VENDOR,
                                                   usb.util.CTRL_RECIPIENT_DEVICE)
        try:
            self._device.ctrl_transfer(request_type, request, value)
        except usb.core.USBError:
            raise CommException("error at communication with the device")

    def _recv_message(self, request):
        request_type = usb.util.build_request_type(usb.util.ENDPOINT_IN, usb.util.CTRL_TYPE_VENDOR,
                                                   usb.util.CTRL_RECIPIENT_DEVICE)
        try:
            response = self._device.ctrl_transfer(request_type, request, 0, 0, 2)
        except usb.core.USBError:
            raise CommException("error at receiving data from the device")

        if len(response) < 2:
            raise CommException("device sent less than two bytes")

        return response[0] + response[1] * 256

    def set_raw_interval(self, raw_interval):
        """Sets the time period of counting cycle. After that time, the counts value is transferred to output buffer
        and accessible for getting. CPI value is cleared during this operation. """
        self._send_message(SET_INTERVAL, int(raw_interval))

    def get_raw_interval(self):
        """Returns the programmed interval."""
        return int(self._recv_message(GET_INTERVAL))

    def set_raw_voltage(self, raw_voltage):
        """Sets the desired Geiger tube supply voltage."""
        self._send_message(SET_VOLTAGE, int(raw_voltage))

    def get_raw_voltage(self):
        """Returns the measured actual Geiger tube supply voltage."""
        return int(self._recv_message(GET_VOLTAGE))

    def get_cpi(self):
        """Returns the number of counts gathered during programmed interval."""
        return float(self._recv_message(GET_CPI))

    def is_count_acknowledged(self):
        """If a new count occurs, this flag is set. The flag is cleared after reading it. This is meant to check for
        counts in real-time. By checking this flag often enough, you can get a precise information about any new
        count."""
        if self._recv_message(ACKNOWLEDGE_UNCHECKED_COUNT) == 1:
            return True
        else:
            return False

    def __str__(self):
        """Returns the string containing all data acquired from the device: actual voltage, current CPI and
        countAcknowledged flag."""
        return "CPI: " + str(self.get_cpi()) + ", supply: " + str(
            self.get_raw_voltage()) + ", count acknowledged: " + str(
            self.is_count_acknowledged())


class Connector(RawConnector):
    """This class wraps a RawCommunicator class to provide human-readable interface in standard units."""

    _tubeSensitivity = TUBE_SENSITIVITY
    _voltDividerFactor = VOLTAGE_DIVIDER_LOWER_RESISTOR / (
            VOLTAGE_DIVIDER_LOWER_RESISTOR + VOLTAGE_DIVIDER_UPPER_RESISTOR)
    _tubeVoltage = TUBE_VOLTAGE
    _configuration = None

    def __init__(self, configuration=None):
        """Optional parameter is configparser instance."""
        super(Connector, self).__init__()
        if configuration is not None:
            self._configuration = configuration

            self._tubeSensitivity = self._load_option('tube_sensitivity', TUBE_SENSITIVITY)
            self._tubeVoltage = self._load_option('tube_voltage', TUBE_VOLTAGE)

            upper_res = self._load_option('upper_resistor', VOLTAGE_DIVIDER_UPPER_RESISTOR)
            lower_res = self._load_option('lower_resistor', VOLTAGE_DIVIDER_LOWER_RESISTOR)

            self._voltDividerFactor = lower_res / (lower_res + upper_res)

    def _load_option(self, option, default_value):
        try:
            return self._configuration.getfloat('device', option)
        except configparser.Error:
            log = logging.getLogger("geiger.usbcomm")
            log.error("Error at loading option '%s'. Assigning default value: %f", option, str(default_value))
            return default_value

    def set_voltage_from_config_file(self):
        """Sets the tube voltage basing on the value written in the config file."""
        self.set_voltage(self._tubeVoltage)

    def get_cpm_and_radiation(self) -> (float, float):
        """Returns a tuple containing CPM and Radiation in respective order."""
        cpm = self.get_cpm()
        radiation = self.get_radiation(cpm)
        return cpm, radiation

    def get_cpm(self) -> float:
        """Returns radiation in counts per minute."""
        return round(self.get_cpi() / self.get_interval() * 60.0, 2)

    def get_radiation(self, cpm=None) -> float:
        """Returns radiation in uSv/h."""
        if cpm is None:
            cpm = self.get_cpm()
        value = (cpm / 60.0) * 10.0 / self._tubeSensitivity
        return round(value, 3)

    def get_interval(self):
        """Returns measuring interval in seconds."""
        return self.get_raw_interval() / TIMER_TICKS_PER_SECOND

    def set_interval(self, seconds):
        """Sets the measuring interval in seconds."""
        if seconds < 1 or seconds > 0xffff / TIMER_TICKS_PER_SECOND:
            raise CommException("interval has to be between 1 and " + str(0xffff / TIMER_TICKS_PER_SECOND) + " seconds")
        self.set_raw_interval(TIMER_TICKS_PER_SECOND * seconds)

    def get_voltage(self) -> int:
        """Returns the measured Geiger tube supply voltage in volts."""
        return int(round(1.1 * self.get_raw_voltage() / (self._voltDividerFactor * 1024.0)))

    def set_voltage(self, volts):
        """Sets the desired Geiger tube supply voltage in volts."""
        if volts < MIN_VOLTAGE or volts > MAX_VOLTAGE:
            raise CommException("voltage has to have value between " + str(MIN_VOLTAGE) + " and "
                                + str(MAX_VOLTAGE) + " volts")
        self.set_raw_voltage(int(self._voltDividerFactor * volts * 1024.0 / 1.1))

    def __str__(self):
        """Returns a string containing all data from the device: CPM, current radioactivity, voltage etc."""

        return "Radiation: " + str(self.get_radiation()) + " uS/h, CPM: " + str(self.get_cpm()) + " int. " + str(
            self.get_interval()) + " s, supply: " + str(self.get_voltage()) + " V, count acknowledged: " + str(
            self.is_count_acknowledged())
