# -*- encoding: utf-8 -*-
'''
 * USB Geiger counter manager
 * 2013 Michał Słomkowski
 * This code is distributed under the terms of GNU General Public License version 3.0.
'''

import Tkinter

class GUIInterface(object):
	def __init__(self, configuration, usbcomm):
		print("gui start" + str(configuration) + str(usbcomm))

	def start(self):
		pass
