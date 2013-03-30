/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 *
 * This code is based on project: hid-custom-rq example from V-USB created by obdev.com
 */

#include "global.h"
#include "usbdrv.h"
#include "requests.h"

#include "geiger_supply.h"
#include "geiger_counter.h"

usbMsgLen_t usbFunctionSetup(uchar data[8]) {
	usbRequest_t *rq = (usbRequest_t *) data;

	static uint16_t result;

	if ((rq->bmRequestType & USBRQ_TYPE_MASK) != USBRQ_TYPE_VENDOR) {
		return 0;
	}

	usbMsgPtr = (unsigned short) &result;

	switch (rq->bRequest) {
	case USB_RQ_GET_VOLTAGE:
		result = GEIGER_ACTUAL_VOLTAGE;
		return 2;
	case USB_RQ_GET_CPI:
		result = countsPerInterval;
		return 2;
	case USB_RQ_GET_INTERVAL:
		result = programmedInterval;
		return 2;
	case USB_RQ_ACKNOWLEDGE_UNCHECKED_COUNT:
		result = uncheckedCount;
		uncheckedCount = false;
		return 2;
	case USB_RQ_SET_VOLTAGE:
		programmedVoltage = rq->wValue.bytes[1] << 8 | rq->wValue.bytes[0];
		return 0;
	case USB_RQ_SET_INTERVAL:
		intervalCount = programmedInterval =  rq->wValue.bytes[1] << 8 | rq->wValue.bytes[0];
		actualCounts = countsPerInterval = 0;
		return 0;
	};

	return 0; /* default for not implemented requests: return no data back to host */
}
