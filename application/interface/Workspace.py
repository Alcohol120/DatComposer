from application.config import *
from application.interface.UI import UI
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *


class Workspace(UI):

    def __init__(self, collection_name):

        self.name = collection_name

        self.composer_box = QGroupBox
        self.structs = QListWidget
        self.controls = {}
        self.browser = QTextBrowser
        self.quick_nav = {}
        self.encoder = {}
        self.decoder = {}
        self.progress = {
            "window": QDialog,
            "current": QProgressBar,
            "total": QProgressBar,
            "texts": {}
        }

        pass

    def setup_workspace(self):

        self._create_tab()
        self._create_composer_box()
        self._create_structures_box()
        self._create_controls()
        self._create_browser()
        self._create_quick_nav()
        self._create_encoder_tabs()
        self._create_progress_dialog()

        pass

    def clear_structs_list(self):

        self.structs.clear()

        pass

    def deselect_encoder_list(self):

        self.encoder["files"].clearSelection()

        pass

    def deselect_decoder_list(self):

        self.decoder["files"].clearSelection()

        pass

    def deselect_structures_list(self):

        self.structs.clearSelection()

        pass

    def add_structure(self, structure):

        self.structs.addItem(structure)

        pass

    def to_dat_enable(self):

        self.controls["to_dat"].setEnabled(1)
        UI.menu_bar_items["File"]["Convert to DAT"].setEnabled(1)

        pass

    def to_dat_disable(self):

        self.controls["to_dat"].setEnabled(0)
        UI.menu_bar_items["File"]["Convert to DAT"].setEnabled(0)

        pass

    def to_txt_enable(self):

        self.controls["to_txt"].setEnabled(1)
        UI.menu_bar_items["File"]["Convert to TXT"].setEnabled(1)

        pass

    def to_txt_disable(self):

        self.controls["to_txt"].setEnabled(0)
        UI.menu_bar_items["File"]["Convert to TXT"].setEnabled(0)

        pass

    @staticmethod
    def test_structure_enable():

        UI.menu_bar_items["File"]["Test Structure"].setEnabled(1)

        pass

    @staticmethod
    def test_structure_disable():

        UI.menu_bar_items["File"]["Test Structure"].setEnabled(0)

        pass

    def set_browser(self, text):

        self.browser.setText(text)

        pass

    def clear_browser(self):

        self.browser.clear()

        pass

    def set_structures_info(self, data):

        html = """
        <table width='100%' cellspacing='0'>
        <tr>
            <td colspan='2' align='center'><strong>{}</strong></td>
        </tr>
        <tr>
            <td align='center'>DAT Files</td>
            <td align='center'>TXT Files</td>
        </tr>
        <tr>
            <td align='center'>{}</td>
            <td align='center'>{}</td>
        </tr>
        </table>""".format(data["title"], data["dat_count"], data["txt_count"])

        if data["note"] != "":
            html += "<p style='color: #777'><i>{}</i></p>".format(data["note"])
        else:
            html += "<br><br>"

        html += "<strong>DAT Files:</strong><br>"

        if len(data["dat_files"]["server"]) > 0:
            html += "<u>Server files</u>"
            rows = self._create_files_rows(data["dat_files"]["server"])
            html += "<table width='100%'>{}</table>".format(rows)

        if len(data["dat_files"]["client"]) > 0:
            html += "<u>Client files</u>"
            rows = self._create_files_rows(data["dat_files"]["client"])
            html += "<table width='100%'>{}</table>".format(rows)

        html += "<br><br><strong>TXT Files:</strong>"
        rows = self._create_files_rows(data["txt_files"])
        html += "<table width='100%'>{}</table>".format(rows)

        self.set_browser(html)

        pass

    def structures_test_result(self, data):

        html = "<p><strong>{} structures tested!</strong></p>".format(str(len(data)))

        success = True

        for item in data:
            if not item["success"]:
                success = False
                html += "<p><span style='color: red'>{}</span><br>{}</p>".format(item["title"], item["error_message"])
            else:
                html += "<p style='color: green'>{}</p>".format(item["title"])

        if success:
            self.alert_success(html, "Structure validation success!")
        else:
            self.alert_error(html, "Structure validation failed!")

        pass

    def show_progress(self, title="Executing..."):

        self.progress["current"].setValue(0)
        self.progress["total"].setValue(0)
        self.progress["texts"]["current"].setText("")
        self.progress["texts"]["total"].setText("")
        self.progress["window"].setWindowTitle(str(title))
        self.progress["window"].show()
        UI.app.processEvents()

        pass

    def set_progress_text_current(self, value):

        self.progress["texts"]["current"].setText(value)

        pass

    def set_progress_text_total(self, value):

        self.progress["texts"]["total"].setText(value)

        pass

    def set_current_progress(self, value):

        self.progress["current"].setValue(value)

        pass

    def set_total_progress(self, value):

        self.progress["total"].setValue(value)

        pass

    # Private Methods

    @staticmethod
    def _create_files_rows(files):

        html = ""

        for file in files:
            if file["exists"]:
                status = "<span style='color: green;'>Ready</span>"
            else:
                status = "<span style='color: red;'>Missing</span>"
            html += "<tr><td>{}</td><td align='right'>{}</td></tr>".format(file["name"], status)

        return html

        pass

    def _create_tab(self):

        tab = QWidget()
        UI.tabs.addTab(tab, self.name)
        UI.tabs_items[self.name] = tab

        pass

    def _create_composer_box(self):

        composer_box = QGroupBox(UI.tabs_items[self.name])
        composer_box.move(5, 5)
        composer_box.setFixedSize(520, 535)
        composer_box.setTitle("Composer")

        self.composer_box = composer_box

        pass

    def _create_structures_box(self):

        # create structures block
        structures_box = QWidget(self.composer_box)
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
        self.structs = strs_list

        pass

    def _create_controls(self):

        # create controls
        to_txt = QCommandLinkButton("To TXT", self.composer_box)
        to_dat = QCommandLinkButton("To DAT", self.composer_box)
        to_edf = QCheckBox("client files to EDF", self.composer_box)

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
        self.controls = {
            "to_txt": to_txt,
            "to_dat": to_dat,
            "to_edf": to_edf,
        }

        pass

    def _create_browser(self):

        label = QLabel("Structure info", self.composer_box)
        label.move(220, 120)

        info_browser = QTextBrowser(self.composer_box)
        info_browser.move(220, 135)
        info_browser.setFixedSize(290, 300)
        info_browser.setFont(QtGui.QFont("Courier", 9))

        self.browser = info_browser

        pass

    def _create_quick_nav(self):

        # create group box
        nav_box = QGroupBox(self.composer_box)
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
        self.quick_nav["cli_dat"] = QPushButton(icon, "Client DAT")
        self.quick_nav["cli_edf"] = QPushButton(icon, "Client EDF")
        self.quick_nav["srv_dat"] = QPushButton(icon, "Server DAT")
        self.quick_nav["txt"] = QPushButton(icon, "TXT")
        self.quick_nav["strs"] = QPushButton(icon, "Structures")
        self.quick_nav["root"] = QPushButton(icon, "Root")

        # set style
        for _, button in self.quick_nav.items():
            button.setStyleSheet("text-align: left")

        # set buttons into layouts
        layout_row1.addWidget(self.quick_nav["cli_dat"])
        layout_row1.addWidget(self.quick_nav["cli_edf"])
        layout_row1.addWidget(self.quick_nav["srv_dat"])
        layout_row2.addWidget(self.quick_nav["txt"])
        layout_row2.addWidget(self.quick_nav["strs"])
        layout_row2.addWidget(self.quick_nav["root"])

        pass

    def _create_encoder_tabs(self):

        # create tabs
        encoder_tabs = QTabWidget(UI.tabs_items[self.name])
        encoder_tabs.setFixedSize(248, 529)
        encoder_tabs.move(530, 11)

        # tabs
        encode_tab = QWidget()
        decode_tab = QWidget()
        encoder_tabs.addTab(encode_tab, "EDF Encode")
        encoder_tabs.addTab(decode_tab, "EDF Decode")

        self._create_encoder_tab(encode_tab, "encode")
        self._create_encoder_tab(decode_tab, "decode")

        pass

    def _create_encoder_tab(self, parent, tab):

        # create layout
        layout = QVBoxLayout(parent)
        if tab == "encode":
            layout.addWidget(QLabel("Select DAT files"))
        else:
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
        if tab == "encode":
            btn_submit = QPushButton("Encode")
        else:
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
        elements = {
            "files": file_list,
            "submit": btn_submit
        }
        if tab == "encode":
            self.encoder = elements
        else:
            self.decoder = elements

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

        self.progress["window"] = dialog
        self.progress["current"] = progress_current
        self.progress["total"] = progress_total
        self.progress["texts"]["current"] = text_1
        self.progress["texts"]["total"] = text_2

        pass

    pass
