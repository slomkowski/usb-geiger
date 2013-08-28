USB Geiger counter
==================

2013 Michał Słomkowski

License: GNU GPL v3.0.

This is a repository of a low-cost USB Geiger counter device using STS-5 tube, ATTiny24 and Python-written host software.

Results can be sent to MySQL database, CSV file, xively.com or defined e-mail address if the radiation is higher than the defined level.

Graphs from my personal Geiger device are available at:
https://xively.com/feeds/120299/

The repository contains:
* *datasheets* - datasheets of parts used in the device, especially the Geiger tube
* *firmare* - source code of firmware for ATTiny24 written in C
* *host/geiger-controller* - simple program in C++ for reading data and writting settings to device
* *host/geiger-manager* - more complex software written in Python. Periodically reads the data from sensor and sends them to cosm.com service, MySQL or CSV file
* *pcb* - printed circuit board layout in Eagle format, schematic in PNG and mirrored board layout for toner transfer




