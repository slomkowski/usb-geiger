/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 */

#ifndef USBCONVENIENTCOMMUNICATOR_H_
#define USBCONVENIENTCOMMUNICATOR_H_

#include "USBRawCommunicator.h"

namespace USB {

	/**
	 * Tube sensitivity parametr at given supply voltage. It is number of pulses per second at the radiation level
	 * 1mR/h = 10 uSv/h.
	 */
	const double TUBE_SENSITIVITY = 25.0;
	const double VOLTAGE_DIVIDER_UPPER_RESISTOR = 2000;
	const double VOLTAGE_DIVIDER_LOWER_RESISTOR = 4.7;

	const int TIMER_TICKS_PER_SECOND = 100;

	const int MIN_VOLTAGE = 50;
	const int MAX_VOLTAGE = 450;

	/**
	 * This class wraps a RawCommunicator class to provide human-readable intervace in standard units.
	 * Warning! These methods are passing CommExceptions from RawCommunicator.
	 */
	class ConvenientCommunicator: public RawCommunicator {
	public:
		/**
		 * Returns radiation in counts per minute.
		 */
		double getCPM();

		/**
		 * Returns radiation in uSv/h.
		 */
		double getRadiation();

		/**
		 * Returns measuring interval in seconds.
		 */
		int getInterval();

		/**
		 * Sets the measuring interval in seconds.
		 */
		void setInterval(int seconds);

		/**
		 * Returns the measured Geiger tube supply voltage in volts.
		 */
		int getVoltage();

		/**
		 * Sets the desired Geiger tube supply voltage in volts.
		 */
		void setVoltage(int volts);

		/**
		 * Returns a string containing all data from the device: CPM, current radioactivity, voltage etc.
		 */
		std::string getStatusString();
	};

} /* namespace USB */
#endif /* USBCONVENIENTCOMMUNICATOR_H_ */
