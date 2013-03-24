/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 */

#ifndef _SUPPLY_H_
#define _SUPPLY_H_

#include "global.h"

void supply_init();

extern volatile uint16_t programmedVoltage;

#define GEIGER_ACTUAL_VOLTAGE ADC

#endif
