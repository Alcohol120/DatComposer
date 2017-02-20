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

    def add_tab(self, name):

        tab = QWidget()
        ui.tabs.addTab(tab, name)
        ui.tabs_items[name] = tab

        # create composer box
        composer_box = QGroupBox(ui.tabs_items[name])
        composer_box.move(5, 5)
        composer_box.setFixedSize(520, 535)
        composer_box.setTitle("Composer")

        ui.composer_box[name] = composer_box

        pass

    def create_structures_box(self, collection):

        # create structures block
        structures_box = QWidget(ui.composer_box[collection])
        structures_box.setFixedSize(220, 525)
        structures_box.move(0, 10)

        # layouts
        v_layout = QVBoxLayout()
        v_layout.addWidget(QLabel("Select structures"))
        h_layout = QHBoxLayout()
        main_layout = QVBoxLayout(structures_box)
        main_layout.addLayout(v_layout)
        main_layout.addLayout(h_layout)

        # create structures list and controls
        strs_list = QListWidget()
        strs_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        btn_sa = QPushButton("Select All")
        btn_ca = QPushButton("Clear All")
        v_layout.addWidget(strs_list)
        h_layout.addWidget(btn_sa)
        h_layout.addWidget(btn_ca)

        # register events
        btn_sa.clicked.connect(strs_list.selectAll)
        btn_ca.clicked.connect(strs_list.clearSelection)

        # add to UI variable
        ui.structs[collection] = strs_list

        pass

    def create_main_controls(self, collection):

        # create controls
        to_txt = QCommandLinkButton("To TXT", ui.composer_box[collection])
        to_dat = QCommandLinkButton("To DAT", ui.composer_box[collection])
        to_edf = QCheckBox("client files to EDF", ui.composer_box[collection])

        # configure
        to_txt.setFixedWidth(120)
        to_dat.setFixedWidth(120)
        to_txt.move(230, 38)
        to_dat.move(380, 38)
        to_edf.move(390, 85)
        to_txt.setEnabled(0)
        to_dat.setEnabled(0)
        to_edf.setChecked(1)

        # add to UI var
        ui.controls[collection] = {
            "to_txt": to_txt,
            "to_dat": to_dat,
            "to_edf": to_edf,
        }

        pass

    def create_info_browser(self, collection):

        label = QLabel("Structure info", ui.composer_box[collection])
        label.move(220, 120)

        info_browser = QTextBrowser(ui.composer_box[collection])
        info_browser.move(220, 135)
        info_browser.setFixedSize(290, 300)

        ui.browser[collection] = info_browser

        pass

    def create_quick_nav(self, collection):

        # create group box
        nav_box = QGroupBox(ui.composer_box[collection])
        nav_box.move(220, 440)
        nav_box.setFixedSize(290, 86)
        nav_box.setTitle("Quick navigation")

        # layout
        layout = QVBoxLayout(nav_box)
        layout_row1 = QHBoxLayout()
        layout_row2 = QHBoxLayout()
        layout.addLayout(layout_row1)
        layout.addLayout(layout_row2)

        # create icon
        icon = QtGui.QIcon(ROOT_PATH + "/application/assets/folder.png")

        # create buttons
        btn1 = QPushButton(icon, "Client DAT")
        btn2 = QPushButton(icon, "Client EDF")
        btn3 = QPushButton(icon, "Server DAT")
        btn4 = QPushButton(icon, "TXT")
        btn5 = QPushButton(icon, "Structures")
        btn6 = QPushButton(icon, "Main")
        btn1.setStyleSheet("text-align: left")
        btn2.setStyleSheet("text-align: left")
        btn3.setStyleSheet("text-align: left")
        btn4.setStyleSheet("text-align: left")
        btn5.setStyleSheet("text-align: left")
        btn6.setStyleSheet("text-align: left")

        # set buttons into layouts
        layout_row1.addWidget(btn1)
        layout_row1.addWidget(btn2)
        layout_row1.addWidget(btn3)
        layout_row2.addWidget(btn4)
        layout_row2.addWidget(btn5)
        layout_row2.addWidget(btn6)

        return [btn1, btn2, btn3, btn4, btn5, btn6]

        pass

    def create_encoder_block(self, collection):

        ui.encoder[collection] = {}

        # create tabs
        encoder_tabs = QTabWidget(ui.tabs_items[collection])
        encoder_tabs.setFixedSize(248, 529)
        encoder_tabs.move(530, 11)

        # tabs
        encode_tab = QWidget()
        decode_tab = QWidget()
        encoder_tabs.addTab(encode_tab, "EDF Encode")
        encoder_tabs.addTab(decode_tab, "EDF Decode")

        # ENCODE
        # create layout
        layout = QVBoxLayout(encode_tab)
        layout.addWidget(QLabel("Select DAT files"))
        v1_layout = QVBoxLayout()
        v2_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        layout.addLayout(v1_layout)
        layout.addLayout(h_layout)
        layout.addLayout(v2_layout)
        # create UI elements
        file_list = QListWidget()
        file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        btn_sa = QPushButton("Select All")
        btn_ca = QPushButton("Clear All")
        btn_submit = QPushButton("Encode")
        btn_submit.setFixedHeight(40)
        btn_submit.setStyleSheet("font-size: 16px")
        # set element to layout
        v1_layout.addWidget(file_list)
        h_layout.addWidget(btn_sa)
        h_layout.addWidget(btn_ca)
        v2_layout.addWidget(btn_submit)
        # register events
        btn_sa.clicked.connect(file_list.selectAll)
        btn_ca.clicked.connect(file_list.clearSelection)
        # set into UI vars
        ui.encoder[collection]["encode"] = {
            "files": file_list,
            "submit": btn_submit
        }

        # DECODE
        # create layout
        layout = QVBoxLayout(decode_tab)
        layout.addWidget(QLabel("Select EDF files"))
        v1_layout = QVBoxLayout()
        v2_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        layout.addLayout(v1_layout)
        layout.addLayout(h_layout)
        layout.addLayout(v2_layout)
        # create UI elements
        file_list = QListWidget()
        file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        btn_sa = QPushButton("Select All")
        btn_ca = QPushButton("Clear All")
        btn_submit = QPushButton("Decode")
        btn_submit.setFixedHeight(40)
        btn_submit.setStyleSheet("font-size: 16px")
        # set element to layout
        v1_layout.addWidget(file_list)
        h_layout.addWidget(btn_sa)
        h_layout.addWidget(btn_ca)
        v2_layout.addWidget(btn_submit)
        # register events
        btn_sa.clicked.connect(file_list.selectAll)
        btn_ca.clicked.connect(file_list.clearSelection)
        # set into UI vars
        ui.encoder[collection]["decode"] = {
            "files": file_list,
            "submit": btn_submit
        }

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

        # fix
        tab = QWidget()
        ui.tabs.addTab(tab, "Main")
        tab.deleteLater()

        pass

builder = Builder()
