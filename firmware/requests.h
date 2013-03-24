/*
 * USB Geiger counter
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
 */

#ifndef __REQUESTS_H_INCLUDED__
#define __REQUESTS_H_INCLUDED__

/**
 * This request causes the device to return the number of counts during programmed interval.
 */
#define USB_RQ_GET_CPI 10

/**
 * Sets the radiation measuring interval (in 20 ms unit).
 */
#define USB_RQ_SET_INTERVAL 20
#define USB_RQ_GET_INTERVAL 21

/**
 * Used to set and get the Geiger tube supply voltage in the ADC value units.
 */
#define USB_RQ_SET_VOLTAGE 30
#define USB_RQ_GET_VOLTAGE 31

/**
 * This request is used in real time host-counter communication. The host pools the counter for new counts.
 * If there is one, the request results 1, otherwise 0.
 */
#define USB_RQ_ACKNOWLEDGE_UNCHECKED_COUNT 40

#endif /* __REQUESTS_H_INCLUDED__ */
