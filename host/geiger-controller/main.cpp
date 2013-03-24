/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 */

#include <iostream>
#include <sstream>

#include "USBConvenientCommunicator.h"
#include "ezOptionParser.hpp"

using namespace std;
using namespace USB;
using namespace ez;

static string geigerReport(ConvenientCommunicator *cc) {
	std::ostringstream sstm;
	sstm << "Radiation: " << cc->getRadiation() << " uS/h\n";
	sstm << "CPM: " << cc->getCPM() << endl;
	sstm << "Interval: " << cc->getInterval() << " s\n";
	sstm << "Tube voltage: " << cc->getVoltage() << " V";
	return sstm.str();
}

int main(int argc, const char **argv) {

	ConvenientCommunicator *usbRaw;
	ezOptionParser opt;

	opt.overview = "USB Geiger Controller (C) 2013 Michał Słomkowski.\n";
	opt.overview += "Program performs low-level operations on USB Geiger hardware.";
	opt.syntax = "geiger-controller [OPTIONS]";
	opt.footer = "If no arguments given, it displays status message containing all parameters.";

	// getters
	opt.add("", 0, 0, 0, "Returns current radiation level in uSv/h", "-r", "--radiation");
	opt.add("", 0, 0, 0, "Returns actual Counts Per Minute value", "-c", "-cpm", "--cpm");
	opt.add("", 0, 0, 0, "Returns Geiger tube supply voltage", "-v", "--voltage");
	opt.add("", 0, 0, 0, "Returns programmed measuring interval", "-i", "--interval");
	opt.add("", 0, 0, 0, "Displays this message", "-h", "-help", "--help");

	// setters
	opt.add("", 0, 1, 0, "Sets new measuring interval in seconds.", "-i", "--interval");
	opt.add("", 0, 1, 0, "Sets new Geiger tube supply voltage in volts.", "-v", "--voltage");

	opt.parse(argc, argv);

	if (opt.isSet("-h")) {
		string usage;
		opt.getUsage(usage);
		cout << usage << endl;
		return 0;
	}

	try {
		usbRaw = new ConvenientCommunicator();
	} catch (CommException &e) {
		cerr << "Error at initializing device: " << e.what() << endl;
		return 1;
	}

	vector<int> list;

	try {
		if (argc <= 1) {
			cout << geigerReport(usbRaw) << endl;
			return 0;
		}

		if (opt.isSet("-v")) {
			opt.get("-v")->getInts(list);
			if (list.size() > 0) {
				usbRaw->setVoltage(list[0]);
			} else {
				cout << usbRaw->getVoltage() << endl;
			}
			return 0;
		}

		if (opt.isSet("-i")) {
			opt.get("-i")->getInts(list);
			if (list.size() > 0) {
				usbRaw->setInterval(list[0]);
			} else {
				cout << usbRaw->getInterval() << endl;
			}
			return 0;
		}

		if (opt.isSet("-cpm")) {
			cout << usbRaw->getCPM() << endl;
			return 0;
		}

		if (opt.isSet("-r")) {
			cout << usbRaw->getRadiation() << endl;
			return 0;
		}

	} catch (CommException &e) {
		cerr << "Error occured: " << e.what() << endl;
		return 1;
	}

	return 0;
}
