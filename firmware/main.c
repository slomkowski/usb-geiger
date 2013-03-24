/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 *
 * This code is based on project: hid-custom-rq example from V-USB created by obdev.com
 */

#include "global.h"

#include <avr/io.h>
#include <avr/wdt.h>
#include <avr/interrupt.h>
#include <util/delay.h>

#include <avr/pgmspace.h>
#include "usbdrv.h"
#include "requests.h"

#include "geiger_supply.h"
#include "geiger_counter.h"

PROGMEM const char usbHidReportDescriptor[22] = { /* USB report descriptor */
0x06, 0x00, 0xff,              // USAGE_PAGE (Generic Desktop)
	0x09, 0x01,                    // USAGE (Vendor Usage 1)
	0xa1, 0x01,                    // COLLECTION (Application)
	0x15, 0x00,                    //   LOGICAL_MINIMUM (0)
	0x26, 0xff, 0x00,              //   LOGICAL_MAXIMUM (255)
	0x75, 0x08,                    //   REPORT_SIZE (8)
	0x95, 0x01,                    //   REPORT_COUNT (1)
	0x09, 0x00,                    //   USAGE (Undefined)
	0xb2, 0x02, 0x01,              //   FEATURE (Data,Var,Abs,Buf)
	0xc0                           // END_COLLECTION
	};
/* The descriptor above is a dummy only, it silences the drivers. The report
 * it describes consists of one byte of undefined data.
 * We don't transfer our data through HID reports, we use custom requests
 * instead.
 */

int main() {
	wdt_enable(WDTO_1S);

	usbInit();
	usbDeviceDisconnect(); // enforce re-enumeration, do this while interrupts are disabled!

	supply_init();
	counter_init();
	led_init();

	sei();
	/* Dirty trick to wait > 250 ms. The ledCounter flag will be set to 0 from interrupt routine TIM0_COMPA
	 * in file geiger_counter.c
	 */
	for (led_off(); led_is_off();); // wait till the led is on

	usbDeviceConnect();

	for (;;) {
		wdt_reset();
		usbPoll();
	}
}

/* ------------------------------------------------------------------------- */
