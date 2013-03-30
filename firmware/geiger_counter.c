/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 */

#include "global.h"
#include <avr/interrupt.h>

#include "geiger_counter.h"

/**
 * The geiger input is on PB2 (PCINT10), which stays at pin-change interrupt 1.
 */

volatile _Bool uncheckedCount = false;

volatile COUNTS_VAR_TYPE countsPerInterval;
volatile COUNTS_VAR_TYPE actualCounts;

volatile uint16_t programmedInterval = 100 * DEFAULT_INTERVAL_SECONDS;

volatile uint8_t ledCounter = 260 / 10; // 300 ms, this variable is used in a tricky way in main.c to wait ~ 300 ms

volatile uint16_t intervalCount;

void counter_init() {
	// pin change interrupt
	PCMSK1 |= (1 << PCINT10);
	GIMSK |= (1 << PCIE1);

	// timer0 setup
	OCR0A = 155; // there will be interrupt every 10 ms
	TIMSK0 = (1 << OCIE0A);
	TCCR0A = (1 << WGM01); // CTC-mode
	TCCR0B = (1 << CS02) | (1 << CS00); // prescaler to 1024
}

ISR(PCINT1_vect, ISR_NOBLOCK) {
	static uint8_t risingEdge = 0xff;

	if (risingEdge) {
		actualCounts++;
		uncheckedCount = true;

		led_off();
		ledCounter = LED_BLINK_TIME / 10;
	}

	risingEdge = ~risingEdge;
}

ISR(TIM0_COMPA_vect, ISR_NOBLOCK) {

	if (ledCounter > 0) {
		ledCounter--;
	} else led_on();

	if (intervalCount != 0) {
		intervalCount--;
		return;
	}

	intervalCount = programmedInterval;
	countsPerInterval = actualCounts;
	actualCounts = 0;
}
