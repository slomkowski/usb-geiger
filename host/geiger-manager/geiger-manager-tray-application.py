#!/usr/bin/env python3
import sys
import time

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox

import updaters
import usbcomm
import utils

app = QApplication(sys.argv)

menu = QMenu()
info_action = menu.addAction("info action")
menu.addSeparator()
exit_action = menu.addAction("Exit application")

exit_action.triggered.connect(app.quit)

tray_icon = QSystemTrayIcon(QIcon("icons8-nuclear-64.png"), parent=app)
tray_icon.setContextMenu(menu)
tray_icon.show()


def set_widgets_content(text):
    info_action.setText(text)
    tray_icon.setToolTip(text)


class GuiUpdater(updaters.BaseUpdater):
    full_name = "GUI Updater"

    def __init__(self, configuration):
        super().__init__(configuration)
        set_widgets_content("Waiting for data from Geiger counter...")

    def update(self, timestamp: time.struct_time, radiation: float = None, cpm: float = None):
        set_widgets_content("Radiation: %.2f uS/h, CPM: %.0f." % (radiation, cpm))


try:
    import monitor

    conf = utils.load_configuration()
    updaters = monitor.find_updaters(conf)
    updaters.append(GuiUpdater(conf))
    comm = usbcomm.Connector(conf)
    monitor = monitor.Monitor(conf, comm, updaters)
except Exception as e:
    msg_box = QMessageBox(QMessageBox.Critical, "Error initializing Geiger Manager", str(e), [QMessageBox.Ok])
    msg_box.buttonClicked.connect(app.quit)

sys.exit(app.exec())
