from application.config import *
from application.interface.ui import ui
from application.interface.builder import builder
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *


class GUI:

    def setup(self, sys_argv):

        app = QApplication(sys_argv)

        builder.build()

        # show the main window
        ui.window.show()

        return app

        pass

    @staticmethod
    def alert_error(message, title="Error"):

        msg = QMessageBox(ui.window)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Critical)
        msg.exec()

        pass

    pass
