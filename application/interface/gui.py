from application.config import *
from application.interface.ui import ui
from application.interface.builder import builder
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
import os


class GUI:

    def setup(self, sys_argv):

        app = QApplication(sys_argv)

        builder.build()

        # show the main window
        ui.window.show()

        return app

        pass

    def add_workspace(self, collection):

        builder.add_tab(collection["name"])
        builder.create_structures_box(collection["name"])
        builder.create_main_controls(collection["name"])
        builder.create_info_browser(collection["name"])
        builder.create_encoder_block(collection["name"])
        qn_buttons = builder.create_quick_nav(collection["name"])

        # register quick nav events
        i = 0
        for btn in qn_buttons:
            if i == 0:
                path = ROOT_PATH + "/" + collection["paths"]["cli_dat"]
            elif i == 1:
                path = ROOT_PATH + "/" + collection["paths"]["cli_edf"]
            elif i == 2:
                path = ROOT_PATH + "/" + collection["paths"]["srv_dat"]
            elif i == 3:
                path = ROOT_PATH + "/" + collection["paths"]["txt"]
            elif i == 4:
                path = ROOT_PATH + "/" + collection["paths"]["structs"]
            elif i == 5:
                path = ROOT_PATH
            btn.clicked.connect(lambda: os.startfile(path))
            i += 1

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
