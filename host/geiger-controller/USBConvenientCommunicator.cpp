/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 */

#include <sstream>
#include <cmath>

#include "USBConvenientCommunicator.h"

static const double voltDividerFactor = USB::VOLTAGE_DIVIDER_LOWER_RESISTOR
	/ (USB::VOLTAGE_DIVIDER_LOWER_RESISTOR + USB::VOLTAGE_DIVIDER_UPPER_RESISTOR);

double USB::ConvenientCommunicator::getCPM() {
	return (double) getCPI() / (double) getInterval() * 60.0;
}

double USB::ConvenientCommunicator::getRadiation() {
	double value = (getCPM() / 60.0) * 10.0 / TUBE_SENSITIVITY;
	// round to 3 decimal places
	return round(value * 1000.0) / 1000.0;
}

int USB::ConvenientCommunicator::getInterval() {
	return getRawInterval() / TIMER_TICKS_PER_SECOND;
}

void USB::ConvenientCommunicator::setInterval(int seconds) {
	if ((seconds < 1) || (seconds > 0xffff / TIMER_TICKS_PER_SECOND)) {
		std::ostringstream sstm;
		sstm << "interval has to be between 1 and " << (0xffff / TIMER_TICKS_PER_SECOND) << " seconds";
		throw CommException(sstm.str());
	}

	setRawInterval(TIMER_TICKS_PER_SECOND * seconds);
}

int USB::ConvenientCommunicator::getVoltage() {
	return round(1.1 * (double) getRawVoltage()) / (voltDividerFactor * 1024.0);
}

void USB::ConvenientCommunicator::setVoltage(int volts) {
	if ((volts < MIN_VOLTAGE) || (volts > MAX_VOLTAGE)) {
		std::ostringstream sstm;
		sstm << "voltage has to have value between " << MIN_VOLTAGE << " and " << MAX_VOLTAGE << " volts";
		throw CommException(sstm.str());
	}

	setRawVoltage(voltDividerFactor * (double) volts * 1024.0 / 1.1);
}

std::string USB::ConvenientCommunicator::getStatusString() {
	std::ostringstream sstm;
	sstm << "Radiation: " << getRadiation() << " uS/h, CPM: " << getCPM() << " (int. " << getInterval()
		<< " s), supply: " << getVoltage() << " V, count acknowledged: " << isCountAcknowledged();
	return sstm.str();
}
