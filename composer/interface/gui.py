from composer.config import *
from composer.interface.ui import ui
from composer.interface.builder import builder
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

    pass
