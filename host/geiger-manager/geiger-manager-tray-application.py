#!/usr/bin/env python3
import sys

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon

app = QApplication(sys.argv)
tray_icon = QSystemTrayIcon(QIcon("icons8-nuclear-64.png"), parent=app)
tray_icon.setToolTip("test trool tip")
tray_icon.show()

menu = QMenu()
exit_action = menu.addAction("Exit")

exit_action.triggered.connect(app.quit)

tray_icon.setContextMenu(menu)

sys.exit(app.exec())
