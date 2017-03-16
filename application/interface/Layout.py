from application.config import *
from application.interface.UI import UI
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
import webbrowser


class Layout(UI):

    def setup(self, sys_argv):

        UI.app = QApplication(sys_argv)

        self._build_main_window()
        self._create_progress_dialog()
        self._create_about_modal()

        UI.window.show()

        pass

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

    def _create_menu_bar(self):

        UI.menu_bar = QMenuBar(UI.window)
        UI.menu_bar.setFixedSize(800, 20)

        menu_file = UI.menu_bar.addMenu("File")
        menu_help = UI.menu_bar.addMenu("Help")

        UI.menu_bar_items = {
            "File": {
                "Convert to TXT": menu_file.addAction("Convert to TXT"),
                "Convert to DAT": menu_file.addAction("Convert to DAT"),
                "Test Structure": menu_file.addAction("Test Structure"),
                "Quit": menu_file.addAction("Quit")
            },
            "Help": {
                "About": menu_help.addAction("About"),
                "Docs": menu_help.addAction("Docs"),
                "Support": menu_help.addAction("Support")
            }
        }

        UI.menu_bar_items["File"]["Convert to TXT"].setEnabled(0)
        UI.menu_bar_items["File"]["Convert to DAT"].setEnabled(0)
        UI.menu_bar_items["File"]["Test Structure"].setEnabled(0)

        UI.menu_bar_items["Help"]["Docs"].triggered.connect(self.open_docs_page)
        UI.menu_bar_items["Help"]["Support"].triggered.connect(self.open_support_page)

        pass

    @staticmethod
    def _create_tabs():

        UI.tabs = QTabWidget(UI.window)
        UI.tabs.move(5, 25)
        UI.tabs.setFixedSize(790, 570)

        # QTabWidget.currentIndex()

        # fix
        tab = QWidget()
        UI.tabs.addTab(tab, "Main")
        tab.deleteLater()

        pass

    def _create_progress_dialog(self):

        dialog = QDialog(UI.window, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        dialog.setWindowTitle("Executing...")
        dialog.setFixedWidth(400)

        layout = QVBoxLayout(dialog)

        progress_current = QProgressBar()
        progress_current.setValue(0)

        progress_total = QProgressBar()
        progress_total.setValue(0)

        text_1 = QLabel("")
        text_2 = QLabel("")

        layout.addWidget(text_1, alignment=QtCore.Qt.AlignBaseline)
        layout.addWidget(progress_current, alignment=QtCore.Qt.AlignBaseline)
        layout.addWidget(text_2, alignment=QtCore.Qt.AlignBaseline)
        layout.addWidget(progress_total, alignment=QtCore.Qt.AlignBaseline)

        cancel = QPushButton("Cancel")
        layout.addWidget(cancel)

        self.progress["window"] = dialog
        self.progress["current"] = progress_current
        self.progress["total"] = progress_total
        self.progress["texts"]["current"] = text_1
        self.progress["texts"]["total"] = text_2
        self.progress["cancel"] = cancel

        pass

    def _create_about_modal(self):

        dialog = QDialog(UI.window, QtCore.Qt.WindowCloseButtonHint)
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        dialog.setWindowTitle("About DATComposer")
        dialog.setFixedWidth(300)

        layout = QVBoxLayout(dialog)

        logo = QLabel()
        logo.setPixmap(QtGui.QPixmap(ROOT_PATH + "/application/assets/logo.png"))
        logo.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(logo)

        layout.addWidget(QLabel())

        row = QLabel("Version: {}".format(str(APP_VERSION)))
        row.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(row)

        row = QLabel("Author: Alcohol120%")
        row.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(row)

        row = QLabel("Email: <span style='color: blue'><u>alcohol120ds@gmail.com</u></span>")
        row.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(row)

        row.mousePressEvent = self.send_mail

        layout.addWidget(QLabel())

        row = QLabel("<span style='color: blue'><u>http://alclab.pro/projects/datcomposer</u></span>")
        row.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(row)

        row.mousePressEvent = self.open_project_page

        self.dialogs["about"] = dialog

        pass

    @staticmethod
    def send_mail(event):

        webbrowser.open("mailto:alcohol120ds@gmail.com?subject=DATComposer")

        pass

    @staticmethod
    def open_project_page(event):

        webbrowser.open_new_tab("http://alclab.pro/projects/datcomposer")

        pass

    @staticmethod
    def open_docs_page(event):

        webbrowser.open_new_tab("http://alclab.pro/projects/datcomposer/docs")

        pass

    @staticmethod
    def open_support_page(event):

        webbrowser.open_new_tab("http://alclab.pro/projects/datcomposer/support")

        pass

    pass
