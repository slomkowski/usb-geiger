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
import signal
import sys
import time

import usbcomm

__version__ = '1.2.0'
__author__ = 'Michał Słomkowski'
__copyright__ = 'GNU GPL v.3.0'

# default config file name
CONFIG_FILE_NAME = 'configuration.ini'
# directories with configuration file
CONFIG_PATH = [".", os.path.dirname(__file__), os.path.expanduser("~/.geiger"), "/etc/geiger"]

CONFIG_PATH = [os.path.realpath(os.path.join(directory, CONFIG_FILE_NAME)) for directory in CONFIG_PATH]


def signal_handler(signum, frame):
    """Handles stopping signals, closes all updaters and threads and exits."""
    if args.monitor:
        global logger
        logger.info("Catched signal no. %d, stopping.", signum)
        global monitor
        monitor.stop()
        logging.shutdown()
        sys.exit(1)


# parse command-line arguments
description = "Geiger manager v. " + __version__ + ', ' + __author__ + ". "
description += """This program is a daemon which monitors constantly the radiation measured by USB Geiger device
and sends the results to cosm.com, MySQL database or CSV file. All configuration is stored in the file '"""
description += CONFIG_FILE_NAME
description += """' which is essential to run. Program uses pyusb library and MySQLdb, if MySQL is enabled."""

parser = argparse.ArgumentParser(description=description)
parser.add_argument("-c", "--config", nargs=1, help="reads given configuration file")
parser.add_argument("-v", "--verbose", action='store_true', help="shows additional information")
parser.add_argument("-b", "--background", action='store_true', help="runs as background process")
group = parser.add_mutually_exclusive_group()
group.add_argument("-m", "--monitor", action='store_true', help="starts program in monitor mode")
group.add_argument("-s", "--status", action='store_true',
                   help="reads data from Geiger device and leaves (enabled by default)")

args = parser.parse_args()

if args.verbose and not args.background:
    print("Geiger manager v. " + __version__ + ', ' + __author__)

# become a daemon and fork
if args.background:
    if os.fork() != 0:
        os._exit(0)

if args.config:
    CONFIG_PATH = [args.config[0]]
    if args.verbose and not args.background:
        print("Using configuration file '%s'" % args.config[0])

# load configuration file
conf = configparser.ConfigParser()

configuration_loaded = False
for filePath in CONFIG_PATH:
    try:
        conf.read(filePath)
        configuration_loaded = True
        if args.verbose and not args.background:
            print("Configuration file loaded from: " + filePath)
        break
    except IOError:
        configuration_loaded = False

if not configuration_loaded:
    print("Error at loading configuration file.", file=sys.stderr)
    sys.exit(1)

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

if not args.background:
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

# register SIGINT (Ctrl-C) signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# start monitor mode
if args.monitor:
    import monitor

    monitor = monitor.Monitor(configuration=conf, usbcomm=comm)
    monitor.start()

    while True:
        time.sleep(5)

# default behavior: display values from Geiger device and leave
print(comm)
sys.exit()
