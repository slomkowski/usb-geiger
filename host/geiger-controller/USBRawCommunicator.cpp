/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 */

#include <libusb-1.0/libusb.h>
#include <string>
#include <sstream>

#include "USBRawCommunicator.h"

using namespace USB;

static const int BUFFER_SIZE = 32;
static const int MESSAGE_TIMEOUT = 2000; // ms

RawCommunicator::RawCommunicator() throw (CommException) {

	devHandle = NULL;

	bool foundGeigerDevice = false;

	libusb_init(NULL);

	libusb_device **listOfDevices;
	ssize_t noOfDevices = libusb_get_device_list(NULL, &listOfDevices);

	for (ssize_t i = 0; i < noOfDevices; i++) {
		struct libusb_device_descriptor desc;

		int status = libusb_get_device_descriptor(listOfDevices[i], &desc);
		if (status < 0) {
			continue;
		}

		if ((desc.idVendor == VENDOR_ID) && (desc.idProduct == DEVICE_ID)) {
			status = libusb_open(listOfDevices[i], &devHandle);
			if (status != 0) {
				continue;
			}

			char vendorString[BUFFER_SIZE] = "", productString[BUFFER_SIZE] = "";

			if ((desc.iManufacturer > 0) && (desc.iProduct > 0)) {
				libusb_get_string_descriptor_ascii(devHandle, desc.iManufacturer, (unsigned char*) vendorString,
					sizeof(vendorString));

				libusb_get_string_descriptor_ascii(devHandle, desc.iProduct, (unsigned char*) productString,
					sizeof(productString));
			}

			if ((VENDOR_NAME.compare(vendorString) == 0) && (DEVICE_NAME.compare(productString) == 0)) {
				foundGeigerDevice = true;
			} else {
				libusb_close(devHandle);
			}
		}
	}

	libusb_free_device_list(listOfDevices, 1);

	if (foundGeigerDevice == false) {
		throw CommException("Geiger counter device not found");
	}
}

void USB::RawCommunicator::sendMessage(Request request, unsigned int value) {
	unsigned char buffer[BUFFER_SIZE];

	if (value > 0xffff) {
		throw CommException("device doesn't support values longer than two bytes");
	}

	int status = libusb_control_transfer(devHandle,
		LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE | LIBUSB_ENDPOINT_OUT, request, value, 0, buffer, 0,
		MESSAGE_TIMEOUT);

	if (status < 0) {
		throw CommException("error at communication with the device");
	}
}

unsigned int USB::RawCommunicator::recvMessage(Request request) {
	unsigned char buffer[BUFFER_SIZE];

	int status = libusb_control_transfer(devHandle,
		LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE | LIBUSB_ENDPOINT_IN, request, 0, 0, buffer,
		sizeof(buffer), MESSAGE_TIMEOUT);

	if (status < 0) {
		throw CommException("error at communication with the device");
	} else if (status < 2) {
		throw CommException("device sent less than two bytes");
	}

	return buffer[0] + buffer[1] * 256;
}

RawCommunicator::~RawCommunicator() {
	libusb_close(devHandle);
	libusb_exit(NULL);
}

void RawCommunicator::setRawInterval(unsigned int rawInterval) throw (CommException) {
	sendMessage(SET_INTERVAL, rawInterval);
}

unsigned int RawCommunicator::getRawInterval() throw (CommException) {
	return recvMessage(GET_INTERVAL);
}

void RawCommunicator::setRawVoltage(unsigned int rawVoltage) throw (CommException) {
	sendMessage(SET_VOLTAGE, rawVoltage);
}

unsigned int RawCommunicator::getRawVoltage() throw (CommException) {
	return recvMessage(GET_VOLTAGE);
}

unsigned int RawCommunicator::getCPI() throw (CommException) {
	return recvMessage(GET_CPI);
}

bool RawCommunicator::isCountAcknowledged() throw (CommException) {
	if (recvMessage(ACKNOWLEDGE_UNCHECKED_COUNT)) {
		return true;
	} else {
		return false;
	}
}

std::string USB::RawCommunicator::getStatusString() {
	std::ostringstream sstm;
	sstm << "CPI: " << getCPI() << ", supply: " << getRawVoltage() << ", count acknowledged: " << isCountAcknowledged();
	return sstm.str();
}
