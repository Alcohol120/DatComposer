from PyQt5 import QtCore
from PyQt5.QtWidgets import *


class UI(QtCore.QObject):

    app = object
    window = object

    menu_bar = object
    menu_bar_items = {}

    tabs = object
    tabs_items = {}
    progress = {
        "window": QDialog,
        "current": QProgressBar,
        "total": QProgressBar,
        "texts": {}
    }

    # signals
    signal_alert_error = QtCore.pyqtSignal(str, str)
    signal_alert_success = QtCore.pyqtSignal(str, str)
    signal_show_progress = QtCore.pyqtSignal(str)
    signal_hide_progress = QtCore.pyqtSignal()
    signal_current_progress_text = QtCore.pyqtSignal(str)
    signal_total_progress_text = QtCore.pyqtSignal(str)
    signal_current_progress = QtCore.pyqtSignal(int)
    signal_total_progress = QtCore.pyqtSignal(int)

    def __init__(self):

        super().__init__()

        # init signals
        self.signal_alert_error.connect(self.alert_error)
        self.signal_alert_success.connect(self.alert_success)
        self.signal_show_progress.connect(self.show_progress)
        self.signal_hide_progress.connect(self.hide_progress)
        self.signal_current_progress_text.connect(self.set_current_progress_text)
        self.signal_total_progress_text.connect(self.set_total_progress_text)
        self.signal_current_progress.connect(self.set_current_progress)
        self.signal_total_progress.connect(self.set_total_progress)

        pass

    @staticmethod
    def get_app_instance():

        return UI.app

        pass

    @staticmethod
    def get_window():

        return UI.window

        pass

    @staticmethod
    def alert_error(message, title="Error"):

        msg = QMessageBox(UI.window)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Critical)
        msg.exec()

        pass

    @staticmethod
    def alert_success(message, title="Success"):

        msg = QMessageBox(UI.window)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Information)
        msg.exec()

        pass

    def show_progress(self, title="Executing..."):

        self.progress["current"].setValue(0)
        self.progress["total"].setValue(0)
        self.progress["texts"]["current"].setText("")
        self.progress["texts"]["total"].setText("")
        self.progress["window"].setWindowTitle(str(title))
        self.progress["window"].show()

        pass

    def hide_progress(self):

        self.progress["window"].hide()

        pass

    def set_current_progress_text(self, value):

        self.progress["texts"]["current"].setText(value)

        pass

    def set_total_progress_text(self, value):

        self.progress["texts"]["total"].setText(value)

        pass

    def set_current_progress(self, value):

        self.progress["current"].setValue(value)

        pass

    def set_total_progress(self, value):

        self.progress["total"].setValue(value)

        pass

    # Private Methods

    pass
