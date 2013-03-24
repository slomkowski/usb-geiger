/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 */

#ifndef COUNTER_H_
#define COUNTER_H_

#include "global.h"

void counter_init();

#define COUNTS_VAR_TYPE uint16_t

extern volatile _Bool uncheckedCount;

extern volatile COUNTS_VAR_TYPE countsPerInterval;
extern volatile COUNTS_VAR_TYPE actualCounts;

extern volatile uint16_t programmedInterval;

// ledCounter is also used in main()
extern volatile uint8_t ledCounter;

#endif /* COUNTER_H_ */
