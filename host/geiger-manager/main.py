#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
"""

import argparse
import configparser
import logging
import os
import sys
import time
import pathlib

import usbcomm
import utils

__version__ = '2.0.0'
__author__ = 'Michał Słomkowski'
__copyright__ = 'GNU GPL v.3.0'


# parse command-line arguments
description = "Geiger manager v. " + __version__ + ', ' + __author__ + ". "
description += """This program is a daemon which monitors constantly the radiation measured by USB Geiger device
and sends the results to radmon.org, MySQL database or CSV file. All configuration is stored in the file '"""
description += utils.CONFIG_FILE_NAME
description += """' which is essential to run. Program uses pyusb library and MySQLdb, if MySQL is enabled."""

parser = argparse.ArgumentParser(description=description)
parser.add_argument("-c", "--config", nargs=1, help="reads given configuration file")
parser.add_argument("-v", "--verbose", action='store_true', help="shows additional information")
group = parser.add_mutually_exclusive_group()
group.add_argument("-m", "--monitor", action='store_true', help="starts program in monitor mode")
group.add_argument("-s", "--status", action='store_true',
                   help="reads data from Geiger device and leaves (enabled by default)")

args = parser.parse_args()

logging.info("Geiger manager v. " + __version__ + ', ' + __author__)

conf = utils.load_configuration(pathlib.Path(args.config[0]) if args.config else None)

try:
    loggingEnabled = conf.getboolean('general', 'log_enabled')
    logFilePath = conf.get('general', 'log_file')
except configparser.Error as exp:
    print("Could not load logging options: %s" % str(exp), file=sys.stderr)
    sys.exit(1)

logger = logging.getLogger("geiger")
logFormatter = logging.Formatter('%(asctime)s %(name)s %(message)s', datefmt='[%Y-%m-%d %H:%M:%S]')
if args.verbose:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.ERROR)

consoleLog = logging.StreamHandler(sys.stdout)
consoleLog.setFormatter(logFormatter)
logger.addHandler(consoleLog)

if not args.monitor:
    loggingEnabled = False

if loggingEnabled:
    try:
        fileLog = logging.FileHandler(logFilePath)
        fileLog.setFormatter(logFormatter)
        logger.addHandler(fileLog)
    except IOError as exp:
        print("Could open log file to write: %s" % str(exp), file=sys.stderr)
        sys.exit(1)

# establish USB connection
try:
    logger.info("Initializing Geiger device...")
    comm = usbcomm.Connector(conf)
except usbcomm.CommException as exp:
    logger.critical("Error at initializing USB device: %s", str(exp))
    sys.exit(1)

# start monitor mode
if args.monitor:
    import monitor

    updaters = monitor.find_updaters(conf)

    monitor = monitor.Monitor(conf, comm, updaters)

    while not monitor.error:
        time.sleep(1)

    logger.critical("Error in monitor: %s", monitor.error)
    sys.exit(2)

# default behavior: display values from Geiger device and leave
print(comm)
