/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 */

#ifndef _GLOBAL_H_
#define _GLOBAL_H_

#ifndef __ASSEMBLER__

#include <stdbool.h>
#include <inttypes.h>
#endif

#include <avr/io.h>

#define PORT(x) XPORT(x)
#define XPORT(x) (PORT##x)
// *** Pin
#define PIN(x) XPIN(x)
#define XPIN(x) (PIN##x)
// *** DDR
#define DDR(x) XDDR(x)
#define XDDR(x) (DDR##x)

#define F_CPU 16000000UL

// LED
#define led_init() (DDRA |= (1 << PA1))
#define led_on() (PORTA &= ~(1 << PA1))
#define led_off() (PORTA |= (1 << PA1))
#define led_is_off() (!(PINA & (1 << PA1)))
#define led_is_on() (PINA & (1 << PA1))

#define DEFAULT_INTERVAL_SECONDS 60
#define DEFAULT_GEIGER_VOLTAGE 395

#define LED_BLINK_TIME 100 // in milliseconds
#endif
