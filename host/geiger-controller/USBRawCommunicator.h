/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 */

#ifndef USBCOMMUNICATOR_H_
#define USBCOMMUNICATOR_H_

#include <libusb-1.0/libusb.h>
#include <stdexcept>
#include <string>

namespace USB {

	const int VENDOR_ID = 0x16c0;
	const int DEVICE_ID = 0x05df;

	const std::string VENDOR_NAME = "slomkowski.eu";
	const std::string DEVICE_NAME = "USB Geiger";

	typedef enum {
		GET_CPI = 10,
		SET_INTERVAL = 20,
		GET_INTERVAL = 21,
		SET_VOLTAGE = 30,
		GET_VOLTAGE = 31,
		ACKNOWLEDGE_UNCHECKED_COUNT = 40
	} Request;

	/**
	 * This exception is thrown if an USB communication error occurs. You can view the error description
	 * by calling exception.what()
	 */
	class CommException: public std::runtime_error {
	public:
		CommException(const std::string& message) :
			std::runtime_error(message) {
		}
	};

	/**
	 * Low level class for Geiger device communication. It handles all libusb calls and supports all low level functions.
	 * Warning! Methods like getVoltage, getInterval don't return values in standard units like seconds or volts,
	 * but device internal representations. You should use this class wrapped by some class transforming them to standard
	 * units.
	 */
	class RawCommunicator {
	public:
		/**
		 * Initiates the class and opens the device. Warning! The constructor assumes that only one Geiger device
		 * is connected to the bus. Otherwise, it opens the first-found one.
		 */
		RawCommunicator() throw (CommException);

		virtual ~RawCommunicator();

		/**
		 * Sets the time period of counting cycle. After that time, the counts value is transferred to output buffer
		 * and accessible for getting.
		 */
		void setRawInterval(unsigned int rawInterval) throw (CommException);
		/**
		 * Returns the programmed interval.
		 */
		unsigned int getRawInterval() throw (CommException);

		/**
		 * Sets the desired Geiger tube supply voltage.
		 */
		void setRawVoltage(unsigned int rawVoltage) throw (CommException);
		/**
		 * Returns the measured actual Geiger tube supply voltage.
		 */
		unsigned int getRawVoltage() throw (CommException);

		/**
		 * Returns the number of counts gathered during programmed interval.
		 */
		unsigned int getCPI() throw (CommException);

		/**
		 * If a new count occures, this flag is set. The flag is cleared after reading it. This is meant to check for
		 * counts in real-time. By checking this flag often enough, you can get a precise information about any new count.
		 */
		bool isCountAcknowledged() throw (CommException);

		/**
		 * Returns the string containing all data acquired from the device: actual voltage, current CPI
		 * and countAcknowledged flag.
		 */
		std::string getStatusString();

	private:
		libusb_device_handle *devHandle;

		void sendMessage(Request request, unsigned int value);
		unsigned int recvMessage(Request request);
	};

}

#endif /* USBCOMMUNICATOR_H_ */
