from application.config import *
from application.interface.UI import UI
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *


class Layout(UI):

    def setup(self, sys_argv):

        UI.app = QApplication(sys_argv)

        self._build_main_window()

        # show the main window
        UI.window.show()

        pass

    # @staticmethod
    # def get_app_instance():
    #
    #     return UI.app
    #
    #     pass
    #
    # @staticmethod
    # def get_window():
    #
    #     return UI.window
    #
    #     pass

    # Private Methods

    def _build_main_window(self):

        # application icon
        app_icon = QtGui.QIcon()
        app_icon.addFile(ROOT_PATH + '/application/assets/icon.png', QtCore.QSize(16, 16))
        app_icon.addFile(ROOT_PATH + '/application/assets/icon.png', QtCore.QSize(24, 24))
        app_icon.addFile(ROOT_PATH + '/application/assets/icon.png', QtCore.QSize(32, 32))
        app_icon.addFile(ROOT_PATH + '/application/assets/icon.png', QtCore.QSize(48, 48))
        app_icon.addFile(ROOT_PATH + '/application/assets/icon.png', QtCore.QSize(256, 256))

        # setting main window
        UI.window = QMainWindow()
        UI.window.setFixedSize(800, 600)
        UI.window.setWindowTitle("{} v{}".format(APP_NAME, APP_VERSION))
        UI.window.setWindowIcon(app_icon)

        # add copyright
        # don't touch this bro =)
        my_copyright = QLabel("By Alcohol120%", UI.window)
        my_copyright.setStyleSheet("color: #777")
        my_copyright.move(710, 18)

        self._create_menu_bar()
        self._create_tabs()

        pass

    @staticmethod
    def _create_menu_bar():

        UI.menu_bar = QMenuBar(UI.window)
        UI.menu_bar.setFixedSize(800, 20)
        UI.menu_bar_items["file"] = UI.menu_bar.addMenu("File")

        pass

    @staticmethod
    def _create_tabs():

        UI.tabs = QTabWidget(UI.window)
        UI.tabs.move(5, 25)
        UI.tabs.setFixedSize(790, 570)

        # fix
        tab = QWidget()
        UI.tabs.addTab(tab, "Main")
        tab.deleteLater()

        pass

    pass
