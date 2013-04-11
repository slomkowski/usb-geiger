Geiger Manager
==============
2013 Michał Słomkowski
License: GNU General Public License ver.3

This program is a daemon which monitors constantly the radiation measured by USB Geiger device and sends the results to cosm.com, MySQL database or CSV file. All configuration is stored in the file 'configuration.ini' which is essential to run. Program uses pyusb library and MySQLdb, if MySQL is enabled.

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
python2 main.py -mb

geiger.sh is a startup script for Debian and derivative systems (like Raspbian). View that file and read the description within to get to know how to use it.

Running on Windows
==================

This program needs Python 2.7 and libraries: pyusb, libusb and MySQL-python if MySQL module will be used.
