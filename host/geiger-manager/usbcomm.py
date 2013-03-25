import usb.core
import usb.util

VENDOR_ID = 0x16c0
DEVICE_ID = 0x05df

VENDOR_NAME = "slomkowski.eu"
DEVICE_NAME = "USB Geiger"

# requests
GET_CPI = 10
SET_INTERVAL = 20
GET_INTERVAL = 21
SET_VOLTAGE = 30
GET_VOLTAGE = 31
ACKNOWLEDGE_UNCHECKED_COUNT = 40

class CommException(Exception):
	pass

class RawConnector(object):
	"""Low level class for Geiger device communication. It handles all libusb calls and supports all low level functions.
	Warning! Methods like getVoltage, getInterval don't return values in standard units like seconds or volts,
	but device internal representations. You should use this class wrapped by some class transforming them to standard
	units.
	"""

	_device = None

	def __init__(self):
		"""Initiates the class and opens the device. Warning! The constructor assumes that only one Geiger device
		is connected to the bus. Otherwise, it opens the first-found one.
		"""

		for dev in usb.core.find(idVendor = VENDOR_ID, idProduct = DEVICE_ID, find_all = True):
			vendorName = usb.util.get_string(dev, 256, dev.iManufacturer)
			deviceName = usb.util.get_string(dev, 256, dev.iProduct)

			if vendorName == VENDOR_NAME and deviceName == DEVICE_NAME:
				self._device = dev
				break

		if self._device is None:
			raise CommException("Geiger counter device not found")

	def _sendMessage(self, request, value):
		if value > 0xffff:
			raise CommException("device doesn't support values longer than two bytes")

		requestType = usb.util.build_request_type(usb.util.ENDPOINT_OUT, usb.util.CTRL_TYPE_VENDOR, usb.util.CTRL_RECIPIENT_DEVICE)
		try:
			self._device.ctrl_transfer(requestType, request, value)
		except usb.core.USBError:
			raise CommException("error at communication with the device")

	def _recvMessage(self, request):
		requestType = usb.util.build_request_type(usb.util.ENDPOINT_IN, usb.util.CTRL_TYPE_VENDOR, usb.util.CTRL_RECIPIENT_DEVICE)
		try:
			response = self._device.ctrl_transfer(requestType, request, 0, 0, 2)
		except usb.core.USBError:
			raise CommException("error at receiving data from the device")

		if len(response) < 2:
			raise CommException("device sent less than two bytes")

		return response[0] + response[1] * 256


	def setRawInterval(self, rawInterval):
		"""Sets the time period of counting cycle. After that time, the counts value is transferred to output buffer
		and accessible for getting. CPI value is cleared during this operation.
		"""
		self._sendMessage(SET_INTERVAL, rawInterval)

	def getRawInterval(self):
		"Returns the programmed interval."
		return self._recvMessage(GET_INTERVAL)

	def setRawVoltage(self, rawVoltage):
		"Sets the desired Geiger tube supply voltage."
		self._sendMessage(SET_VOLTAGE, rawVoltage)

	def getRawVoltage(self):
		"Returns the measured actual Geiger tube supply voltage."
		return self._recvMessage(GET_VOLTAGE)

	def getCPI(self):
		"Returns the number of counts gathered during programmed interval."
		return self._recvMessage(GET_CPI)

	def isCountAcknowledged(self):
		"""If a new count occures, this flag is set. The flag is cleared after reading it. This is meant to check for
		counts in real-time. By checking this flag often enough, you can get a precise information about any new count.
		"""
		return self._recvMessage(ACKNOWLEDGE_UNCHECKED_COUNT)

	def __str__(self):
		"""Returns the string containing all data acquired from the device: actual voltage, current CPI
		and countAcknowledged flag."""
		return "CPI: " + str(self.getCPI()) + ", supply: " + str(self.getRawVoltage()) + ", count acknowledged: " + str(self.isCountAcknowledged())
