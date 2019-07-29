# USB Geiger counter

2013 Michał Słomkowski

License: GNU GPL v3.0.

This is a repository of a low-cost USB Geiger counter device using STS-5 tube, ATTiny24 and Python-written host software.

Results can be sent to MySQL database, CSV file, ~~xively.com~~ or defined e-mail address if the radiation level is above the defined threshold.

Project was published in Polish hobby electronics periodic: *Elektronika dla Wszystkich* 10/2013, the article [available here](https://serwis.avt.pl/manuals/AVT3074.pdf).

The repository contains:
* *datasheets* - datasheets of components used in the device, especially the Geiger tube
* *firmare* - source code of firmware for ATTiny24, written in C
* *host/geiger-controller* - simple program in C++ for reading data and writing the settings to the device
* *host/geiger-manager* - more complex software written in Python. Periodically reads the data from sensor and sends them to MySQL or CSV file
* *pcb* - printed circuit board layout in Eagle format, schematic in PNG and mirrored board layout for toner transfer
