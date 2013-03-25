USB Geiger counter
2013 Michał Słomkowski

Licencja GNU GPL w wersji 3.0.

Kod licznika Geigera dla procesora AVR ATTiny24A. Wymagane AVR-GCC i avr-libc. Makefile udostępnia reguły 'make burn' oraz 'make burn_fuses' dla programatora avrdoper i używa do tego celu avrdude. Kod jest bardzo ciasny, dla kompilatora avr-gcc w wersji 4.7.2 zajętość pamięci wynosi 2040 bajtów. Dołożenie jakiejkolwiek funkcjonalności jest raczej niemożliwe.

Kod wykorzystuje bibliotekę programowego interfejsu USB V-USB pochodzącą z obdev.com.
