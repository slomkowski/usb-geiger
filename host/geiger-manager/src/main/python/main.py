import logging
import sys
import time

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QMessageBox
from fbs_runtime.application_context.PyQt5 import ApplicationContext

import updaters
import usbcomm
import utils

if __name__ == '__main__':
    application_context = ApplicationContext()

    menu = QMenu()
    info_action = menu.addAction("info action")
    menu.addSeparator()
    exit_action = menu.addAction("Exit application")

    exit_action.triggered.connect(application_context.app.quit)
    icon_path = application_context.get_resource("yellow.png")
    tray_icon = QSystemTrayIcon(QIcon(str(icon_path)), parent=application_context.app)
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
        logging.critical("Closing application because of initialization error.", exc_info=e)
        QMessageBox.critical(None, "Geiger Manager error",
                             "Error initializing Geiger Manager: %s. Closing application." % e)
        sys.exit(1)

    exit_code = application_context.app.exec_()
    sys.exit(exit_code)
