Geiger Manager
==============
2013 Michał Słomkowski
License: GNU General Public License ver.3

This program is a daemon which monitors constantly the radiation measured by USB Geiger device and sends the results to xively.com, MySQL database, CSV file or e-mail. All configuration is stored in the file 'configuration.ini' which is essential to run. Program uses pyusb library and MySQLdb, if MySQL is enabled.

Optional arguments:
*  -h, --help            show this help message and exit
* -c CONFIG, --config CONFIG
                        reads given configuration file
*  -v, --verbose         shows additional information
*  -b, --background      runs as background process
*  -m, --monitor         starts program in monitor mode
*  -s, --status          reads data from Geiger device and leaves (enabled by
                        default)

To start measuring as a daemon, type:
python3 main.py -mb

geiger.sh is a startup script for Debian and derivative systems (like Raspbian). View that file and read the description within to get to know how to use it.

Running on Windows
==================

This program needs Python 3.5 and libraries: pyusb, libusb and MySQL-python if MySQL module will be used.


## Buidling on Windows

To install:
* Python 3.6
* http://sourceforge.net/projects/libusb-win32/files/libusb-win32-releases/1.2.6.0/




```
python3 -m venv venv
call venv\Scripts\activate.bat

```
