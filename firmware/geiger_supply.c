/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 */

#include "global.h"

#include <avr/interrupt.h>
#include <util/delay.h>
#include <avr/cpufunc.h>
#include <avr/pgmspace.h>

#include <stdlib.h>

#include "geiger_supply.h"

#define PWM_REG OCR1BL

#define PWM_MAX 220
#define PWM_MIN 20
#define PWM_STEP 3

#define VOLTAGE_DIVIDER_UPPER_RESISTOR 2000.0
#define VOLTAGE_DIVIDER_LOWER_RESISTOR 4.7 

// the macro calculates the ADC setting from desired voltage based on ADC equation and voltage-divider values.
#define VOLTAGE_TO_ADC(vol) ((((VOLTAGE_DIVIDER_LOWER_RESISTOR / (VOLTAGE_DIVIDER_LOWER_RESISTOR + \
	VOLTAGE_DIVIDER_UPPER_RESISTOR)) * (double) vol) * 1024) / 1.1)

// this is not voltage
volatile uint16_t programmedVoltage = VOLTAGE_TO_ADC(DEFAULT_GEIGER_VOLTAGE);

void supply_init() {
	// initialization is made directly on register names. I think is more clean than declaring some crazy-named macros for them.
	DDR(A) |= (1 << PA5); // set PA5 as output
	TCCR1A = (1 << COM1B1) | (1 << WGM10); // phase-correct 8-bit
	TCCR1B = (1 << CS11); // by 8

	// Internal 1.1V voltage reference, input on PA3 enabled
	ADMUX = (1 << REFS1) | (1 << MUX1) | (1 << MUX0);

	// disable digital input buffer on PA3
	DIDR0 = (1 << ADC3D);

	// enable ADC, start conversion, set prescaler to 128 - ADC freq: ~ 125kHz, triggered from Timer0
	ADCSRA = (1 << ADEN) | (1 << ADSC) | (1 << ADATE) | (1 << ADIE) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0);

	// set the ADC trigger as Timer 0 compare match. It starts the conversion every 20 ms
	ADCSRA |= ADCSRB |= (1 << ADTS1) | (1 << ADTS0);
}

ISR(ADC_vect, ISR_NOBLOCK) {
	if (ADC > programmedVoltage) {
		PWM_REG -= PWM_STEP;
	} else if (ADC < programmedVoltage) {
		PWM_REG += PWM_STEP;
	}

	if (PWM_REG > PWM_MAX) PWM_REG = PWM_MAX;
	else if (PWM_REG < PWM_MIN) PWM_REG = PWM_MIN;
}
