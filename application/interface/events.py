from application.config import *
from application.interface.ui import ui
from PyQt5 import QtCore
from PyQt5 import QtGui


class Events:

    def __init__(self, collection):

        self.collection = collection

        pass

    def register(self):

        ui.app.focusWindowChanged.connect()

        pass

    pass
