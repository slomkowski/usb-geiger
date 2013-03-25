#!/usr/bin/python2

import usbcomm

comm = usbcomm.RawConnector()

print("test")
print(comm.getRawVoltage())

comm.setRawInterval(13000)

print(comm)
