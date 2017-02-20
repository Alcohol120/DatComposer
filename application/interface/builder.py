from application.config import *
from application.interface.ui import ui
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *


class Builder:

    def build(self):

        # application icon
        app_icon = QtGui.QIcon()
        app_icon.addFile(ROOT_PATH + '/application/assets/icon.png', QtCore.QSize(16, 16))
        app_icon.addFile(ROOT_PATH + '/application/assets/icon.png', QtCore.QSize(24, 24))
        app_icon.addFile(ROOT_PATH + '/application/assets/icon.png', QtCore.QSize(32, 32))
        app_icon.addFile(ROOT_PATH + '/application/assets/icon.png', QtCore.QSize(48, 48))
        app_icon.addFile(ROOT_PATH + '/application/assets/icon.png', QtCore.QSize(256, 256))

        # setting main window
        ui.window = QMainWindow()
        ui.window.setFixedSize(800, 600)
        ui.window.setWindowTitle("{} v{}".format(APP_NAME, APP_VERSION))
        ui.window.setWindowIcon(app_icon)

        # add copyright
        # don't touch this bro =)
        copyright = QLabel("By Alcohol120%", ui.window)
        copyright.setStyleSheet("color: #777")
        copyright.move(710, 18)

        self._create_menu_bar()
        self._create_tabs()

        pass

    def _create_menu_bar(self):

        ui.menu_bar = QMenuBar(ui.window)
        ui.menu_bar.setFixedSize(800, 20)
        ui.menu_bar_items["file"] = ui.menu_bar.addMenu("File")

        pass

    def _create_tabs(self):

        ui.tabs = QTabWidget(ui.window)
        ui.tabs.move(5, 25)
        ui.tabs.setFixedSize(790, 570)
        tab = QWidget()
        ui.tabs.addTab(tab, "Main")
        ui.tabs_items["blank"] = tab

        pass

builder = Builder()
