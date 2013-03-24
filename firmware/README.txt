USB Geiger counter
2013 Michał Słomkowski

License: GNU GPL v3.0.

Geiger counter firmware source code for ATTiny24A. AVR-GCC and avr-libc required for compiling. The code is tight; using avr-gcc 4.7.2 gives the 2040 bytes result file. Adding any new features is rather impossible. Makefile provides additional rules: 'make burn' and 'make burn_fuses' using avrdude configured for avrdoper programmer.

The code contains USB interface software library V-USB from obdev.com.

