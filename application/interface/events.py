from application.config import *
from application.interface.ui import ui
from PyQt5 import QtCore
from PyQt5 import QtGui


class Events:

    def __init__(self, collection_name, controller):

        self.collection_name = collection_name
        self.controller = controller
        self.register()

        pass

    def register(self):

        ui.app.focusWindowChanged.connect(self.controller.window_focused)

        pass

    pass
