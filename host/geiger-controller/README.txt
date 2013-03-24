USB Geiger counter
2013 Michał Słomkowski

License: GNU GPL v3.0.

Program ten udostępnia wszystkie funkcje licznika Geigera z poziomu linii komend. Listę można sprawdzić komendą:

Program provides simple command-line interface to all functions of Geiger device. To display the full list, type:

./geiger-controller --help

The program was written in C++ and libusbx, which is a fork of libusb-1.0 and should stay compatible with it. The code was compiled and run on Linux box, but there's should be no problems with running it on Windows. The program is finished, for more advanced functions like logging to cosm.com or SQL database, check Python script in other directory.
