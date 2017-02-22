from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *


class UI:

    app = object
    window = object

    menu_bar = object
    menu_bar_items = {}

    tabs = object
    tabs_items = {}

    @staticmethod
    def alert_error(message, title="Error"):

        msg = QMessageBox(UI.window)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Critical)
        msg.exec()

        pass

    pass
