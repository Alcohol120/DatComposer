from application.config import *
from application.interface.ui import ui
from application.interface.builder import builder
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
import os


class GUI:

    def setup(self, sys_argv):

        ui.app = QApplication(sys_argv)

        builder.build()

        # show the main window
        ui.window.show()

        return ui.app

        pass

    def setup_workspace(self, collection):

        builder.add_tab(collection["name"])
        builder.create_structures_box(collection["name"])
        builder.create_main_controls(collection["name"])
        builder.create_info_browser(collection["name"])
        builder.create_encoder_block(collection["name"])
        quick_nav = builder.create_quick_nav(collection["name"])

        # register quick nav events
        quick_nav[0].clicked.connect(lambda: self.open_catalog(ROOT_PATH + "/" + collection["paths"]["cli_dat"]))
        quick_nav[1].clicked.connect(lambda: self.open_catalog(ROOT_PATH + "/" + collection["paths"]["cli_edf"]))
        quick_nav[2].clicked.connect(lambda: self.open_catalog(ROOT_PATH + "/" + collection["paths"]["srv_dat"]))
        quick_nav[3].clicked.connect(lambda: self.open_catalog(ROOT_PATH + "/" + collection["paths"]["txt"]))
        quick_nav[4].clicked.connect(lambda: self.open_catalog(ROOT_PATH + "/" + collection["paths"]["structs"]))
        quick_nav[5].clicked.connect(lambda: self.open_catalog(ROOT_PATH))

        pass

    def open_catalog(self, path):

        if os.path.isdir(path):
            os.startfile(path)
        else:
            self.alert_error("Can't find catalog!<br>" + path)

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
