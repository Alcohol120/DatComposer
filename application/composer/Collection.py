from application.config import *
from application.interface.Workspace import Workspace
from application.composer.Structure import Structure
from application.composer.DATFile import DATFile
from application.composer.EDFFile import EDFFile
import os
import re
import math
import time
import datetime
import hashlib
import threading


class Collection:

    def __init__(self, data):

        self.name = data["name"]
        self.paths = data["paths"]

        self.ui = Workspace(data["name"])

        self.structures = {}
        self.client_dat_files = {}
        self.client_edf_files = {}
        self.structs_hash = self._get_structs_hash()
        self.client_dat_hash = self._get_dat_hash()
        self.client_edf_hash = self._get_edf_hash()

        # tasks
        self.task_type = 0
        self.task_queue = []
        self.task_steps = 0
        self.task_current = 0

        self.prepare_catalogs()
        self.ui.setup_workspace()

        self.reload_structures()
        self.reload_client_dat()
        self.reload_client_edf()

        self._register_events()

        pass

    def prepare_catalogs(self):

        if not self._check_catalogs():
            self._create_catalogs()

        pass

    def reload_structures(self):

        self.ui.clear_structs_list()

        files = self._get_structure_files()

        for file in files:
            structure = Structure(file, self.paths)
            structure.set_callbacks({
                "alert_error": self.emit_alert_error,
                "current_progress": self.emit_current_progress,
                "total_progress": self.emit_total_progress,
                "current_progress_text": self.emit_current_progress_text
            })
            if structure.load():
                self.structures[file.replace(".json", "")] = structure
                self.ui.add_structure(structure.get_name())
            else:
                del structure

        pass

    def reload_client_dat(self):

        self.ui.clear_client_dat()
        files = self._get_client_files("dat")

        for file in files:
            file_path = ROOT_PATH + "/" + self.paths["cli_dat"] + "/" + file
            self.client_dat_files[file] = DATFile(file, file_path, self.paths)
            self.client_dat_files[file].set_callbacks({
                "current_progress": self.emit_current_progress
            })
            self.ui.add_client_dat(file)

        pass

    def reload_client_edf(self):

        self.ui.clear_client_edf()
        files = self._get_client_files("edf")

        for file in files:
            file_path = ROOT_PATH + "/" + self.paths["cli_edf"] + "/" + file
            self.client_edf_files[file] = EDFFile(file, file_path, self.paths)
            self.client_edf_files[file].set_callbacks({
                "current_progress": self.emit_current_progress
            })
            self.ui.add_client_edf(file)

        pass

    def validate_selected_structures(self):

        items = self.ui.structs.selectedItems()

        if len(items) > 0:
            result = []
            for item in items:
                structure = self.structures[item.text()]
                test = structure.validate()
                test["name"] = structure.get_name()
                result.append(test)

            self.ui.structures_test_result(result)

        pass

    def convert_to_txt(self):

        items = self.ui.structs.selectedItems()

        self._reset_task()

        if len(items) > 0:

            self.task_type = 1
            self.task_steps = len(items)

            # validate structures
            for item in items:
                test_result = self.structures[item.text()].validate()
                if not test_result["success"]:
                    error = "<p><span style='color: red;'>{}</span></p>".format(test_result["title"])
                    error += test_result["error_message"]
                    self.ui.alert_error(error, test_result["error_type"])
                    return False

            # prepare task
            for item in items:
                struct = self.structures[item.text()]
                self.task_queue.append(struct.get_name())

            # show progress bar
            self.ui.signal_show_progress.emit("Converting to TXT...")

            # start task
            thread = threading.Thread(target=self._start_tasks_to_txt)
            thread.setDaemon(True)
            thread.start()

        return True

        pass

    def convert_to_dat(self):

        items = self.ui.structs.selectedItems()

        self._reset_task()

        if len(items) > 0:

            self.task_type = 1
            self.task_steps = len(items)

            # validate structures
            for item in items:
                test_result = self.structures[item.text()].validate()
                if not test_result["success"]:
                    error = "<p><span style='color: red;'>{}</span></p>".format(test_result["title"])
                    error += test_result["error_message"]
                    self.ui.alert_error(error, test_result["error_type"])
                    return False

            # prepare task
            for item in items:
                struct = self.structures[item.text()]
                self.task_queue.append(struct.get_name())

            # show progress bar
            self.ui.signal_show_progress.emit("Converting to DAT...")

            # start task
            thread = threading.Thread(target=self._start_tasks_to_dat)
            thread.setDaemon(True)
            thread.start()

        return True

        pass

    def client_encode_event(self):

        items = self.ui.encoder["files"].selectedItems()

        self._reset_task()

        if len(items) > 0:

            self.task_type = 2
            self.task_steps = len(items)

            # prepare task
            for item in items:
                self.task_queue.append(item.text())

            # show progress bar
            self.ui.signal_show_progress.emit("EDF Encoding...")

            # start task
            thread = threading.Thread(target=self._start_task_encode)
            thread.setDaemon(True)
            thread.start()

        pass

    def client_decode_event(self):

        items = self.ui.decoder["files"].selectedItems()

        self._reset_task()

        if len(items) > 0:

            self.task_type = 3
            self.task_steps = len(items)

            # prepare task
            for item in items:
                self.task_queue.append(item.text())

            # show progress bar
            self.ui.signal_show_progress.emit("EDF Decoding...")

            # start task
            thread = threading.Thread(target=self._start_task_decode)
            thread.setDaemon(True)
            thread.start()

        pass

    def cancel_current_task(self):

        for task in self.task_queue:
            if self.task_type == 1:
                self.structures[task].cancel_task()
            elif self.task_type == 2:
                self.client_dat_files[task].cancel_task()
            elif self.task_type == 3:
                self.client_edf_files[task].cancel_task()
            else:
                break

        pass

    def reset_user_actions(self):

        self.ui.clear_browser()
        self.ui.deselect_encoder_list()
        self.ui.deselect_decoder_list()
        self.ui.deselect_structures_list()

        pass

    def emit_alert_error(self, message, title=""):

        if title == "":
            self.ui.signal_alert_error.emit(message)
        else:
            self.ui.signal_alert_error.emit(message, title)

        pass

    def emit_current_progress(self, value):

        self.ui.signal_current_progress.emit(value)

        pass

    def emit_total_progress(self, value):

        self.ui.signal_total_progress.emit(value)

        pass

    def emit_current_progress_text(self, value):

        self.ui.signal_current_progress_text.emit(value)

        pass

    # Private Methods

    def _start_tasks_to_txt(self):

        start_time = time.time()

        for task in self.task_queue:
            self.task_current += 1
            total_text = "Structure: {} ... {}/{}".format(task, str(self.task_current), str(self.task_steps))
            self.ui.signal_total_progress_text.emit(total_text)
            result = self.structures[task].to_txt()
            if not result["success"]:
                self.ui.signal_hide_progress.emit()
                self.ui.signal_alert_error.emit(result["error"], result["title"])
                return False

        # completed
        self.ui.signal_hide_progress.emit()
        working_time = math.floor(time.time() - start_time)
        working_time = datetime.timedelta(seconds=working_time)
        message = "{} structures converted to TXT!<br>". format(str(len(self.task_queue)))
        message += "Completed by: {}".format(working_time)
        self.ui.signal_alert_success.emit(message, "Success")

        return True

        pass

    def _start_tasks_to_dat(self):

        start_time = time.time()
        to_edf_checked = self.ui.to_edf_checked()

        for task in self.task_queue:
            self.task_current += 1
            total_text = "Structure: {} ... {}/{}".format(task, str(self.task_current), str(self.task_steps))
            self.ui.signal_total_progress_text.emit(total_text)
            result = self.structures[task].to_dat(to_edf_checked)
            if not result["success"]:
                self.ui.signal_hide_progress.emit()
                self.ui.signal_alert_error.emit(result["error"], result["title"])
                return False

        # completed
        self.ui.signal_hide_progress.emit()
        working_time = math.floor(time.time() - start_time)
        working_time = datetime.timedelta(seconds=working_time)
        message = "{} structures converted to DAT!<br>". format(str(len(self.task_queue)))
        message += "Completed by: {}".format(working_time)
        self.ui.signal_alert_success.emit(message, "Success")

        return True

        pass

    def _start_task_encode(self):

        start_time = time.time()

        self.ui.signal_total_progress_text.emit("Encoding...")

        for task in self.task_queue:
            self.task_current += 1
            self.ui.signal_current_progress_text.emit("{}...".format(task))

            dat_file = self.client_dat_files[task]
            result = dat_file.encode()
            dat_file.reset()
            if not result:
                self.ui.signal_hide_progress.emit()
                self.ui.signal_alert_error.emit("Can't encode file!<br>{}".format(
                    dat_file.get_full_path()),
                    "Encoding error!"
                )
                return False

            edf_name = task.replace(".dat", ".edf")
            if edf_name not in self.client_edf_files:
                edf_file = self._init_edf_file(edf_name)
            else:
                edf_file = self.client_edf_files[edf_name]
            if not edf_file.write(result):
                self.ui.signal_hide_progress.emit()
                self.ui.signal_alert_error.emit("Can't save encoded file!<br>{}".format(
                    edf_file.get_full_path()),
                    "Encoding error!"
                )
                return False
            self.ui.signal_total_progress.emit(self.task_current / (self.task_steps / 100))

        # completed
        self.ui.signal_hide_progress.emit()
        working_time = math.floor(time.time() - start_time)
        working_time = datetime.timedelta(seconds=working_time)
        message = "{} files encoded!<br>".format(str(len(self.task_queue)))
        message += "Completed by: {}".format(working_time)
        self.ui.signal_alert_success.emit(message, "Success")

        return True

        pass

    def _start_task_decode(self):

        start_time = time.time()

        self.ui.signal_total_progress_text.emit("Decoding...")

        for task in self.task_queue:
            self.task_current += 1
            self.ui.signal_current_progress_text.emit("{}...".format(task))

            edf_file = self.client_edf_files[task]
            result = edf_file.decode()
            edf_file.reset()
            if not result:
                self.ui.signal_hide_progress.emit()
                self.ui.signal_alert_error.emit("Can't encode file!<br>{}".format(
                    edf_file.get_full_path()),
                    "Encoding error!"
                )
                return False

            dat_name = task.replace(".edf", ".dat")
            if dat_name not in self.client_dat_files:
                dat_file = self._init_dat_file(dat_name)
            else:
                dat_file = self.client_dat_files[dat_name]
            if not dat_file.write(result):
                self.ui.signal_hide_progress.emit()
                self.ui.signal_alert_error.emit("Can't save decoded file!<br>{}".format(
                    dat_file.get_full_path()),
                    "Encoding error!"
                )
                return False
            self.ui.signal_total_progress.emit(self.task_current / (self.task_steps / 100))

        # completed
        self.ui.signal_hide_progress.emit()
        working_time = math.floor(time.time() - start_time)
        working_time = datetime.timedelta(seconds=working_time)
        message = "{} files decoded!<br>".format(str(len(self.task_queue)))
        message += "Completed by: {}".format(working_time)
        self.ui.signal_alert_success.emit(message, "Success")

        return True

        pass

    def _check_catalog(self, catalog):

        if not os.path.isdir(ROOT_PATH + "/" + self.paths[catalog]):
            return False
        else:
            return True

        pass

    def _check_catalogs(self):

        for _, path in self.paths.items():
            if not os.path.isdir(ROOT_PATH + "/" + path):
                return False

        return True

        pass

    def _create_catalogs(self):

        for _, path in self.paths.items():
            if not os.path.isdir(ROOT_PATH + "/" + path):
                try:
                    os.makedirs(ROOT_PATH + "/" + path)
                except PermissionError:
                    self.ui.alert_error("Can't create collection catalogs!", "Filesystem error!")

        pass

    def _get_structure_files(self):

        if not self._check_catalog("structs"):
            return []

        path = ROOT_PATH + "/" + self.paths["structs"]

        files = os.listdir(path)

        structs = []

        for file in files:
            if not os.path.isfile(path + "/" + file):
                continue
            if re.search(FILE_EXT_RE("json"), file) is None:
                continue
            structs.append(file)

        return structs

        pass

    def _get_client_files(self, file_type="dat"):

        if file_type != "dat" and file_type != "edf":
            return []

        if not self._check_catalog("cli_" + file_type):
            return []

        path = ROOT_PATH + "/" + self.paths["cli_" + file_type]

        def list_catalog(catalog=""):

            scan_in = path
            if catalog != "":
                scan_in += "/" + catalog

            items = os.listdir(scan_in)

            sub = []
            files = []

            for item in items:
                if os.path.isfile(scan_in + "/" + item):
                    if re.search(FILE_EXT_RE(file_type), item) is None:
                        continue
                    file = catalog + "/" + item
                    files.append(file.strip("/"))
                else:
                    sub.append(item)

            for sub_catalog in sub:
                catalog += "/" + sub_catalog
                files.extend(list_catalog(catalog.strip("/")))

            return files

            pass

        return list_catalog()

        pass

    def _get_structs_hash(self):

        if not self._check_catalog("structs"):
            return ""

        structs_path = ROOT_PATH + "/" + self.paths["structs"]

        files = self._get_structure_files()

        times = ""

        for file in files:
            times += str(os.path.getmtime(structs_path + "/" + file))

        if times == "":
            return ""

        times = times.encode("utf-8")
        times_hash = hashlib.md5()
        times_hash.update(times)

        return times_hash.hexdigest()

        pass

    def _get_dat_hash(self):

        if not self._check_catalog("cli_dat"):
            return ""

        dat_path = ROOT_PATH + "/" + self.paths["cli_dat"]

        files = self._get_client_files("dat")

        times = ""

        for file in files:
            times += str(os.path.getmtime(dat_path + "/" + file))

        if times == "":
            return ""

        times = times.encode("utf-8")
        times_hash = hashlib.md5()
        times_hash.update(times)

        return times_hash.hexdigest()

        pass

    def _get_edf_hash(self):

        if not self._check_catalog("cli_edf"):
            return ""

        edf_path = ROOT_PATH + "/" + self.paths["cli_edf"]

        files = self._get_client_files("edf")

        times = ""

        for file in files:
            times += str(os.path.getmtime(edf_path + "/" + file))

        if times == "":
            return ""

        times = times.encode("utf-8")
        times_hash = hashlib.md5()
        times_hash.update(times)

        return times_hash.hexdigest()

        pass

    def _register_events(self):

        app = self.ui.get_app_instance()

        # quick navigation events
        self._quick_nav_events()
        # window focused event
        app.focusWindowChanged.connect(self._window_focus_event)
        # structure selection event
        self.ui.structs.itemSelectionChanged.connect(self._structure_selected_event)
        # convert events
        self.ui.controls["to_dat"].clicked.connect(self.convert_to_dat)
        self.ui.controls["to_txt"].clicked.connect(self.convert_to_txt)
        # encoder/decoder events
        self.ui.encoder["submit"].clicked.connect(self.client_encode_event)
        self.ui.decoder["submit"].clicked.connect(self.client_decode_event)

        pass

    def _quick_nav_events(self):

        self.ui.quick_nav["cli_dat"].clicked.connect(lambda: (
            self._open_catalog(ROOT_PATH + "/" + self.paths["cli_dat"])
        ))
        self.ui.quick_nav["cli_edf"].clicked.connect(lambda: (
            self._open_catalog(ROOT_PATH + "/" + self.paths["cli_edf"])
        ))
        self.ui.quick_nav["srv_dat"].clicked.connect(lambda: (
            self._open_catalog(ROOT_PATH + "/" + self.paths["srv_dat"])
        ))
        self.ui.quick_nav["txt"].clicked.connect(lambda: (
            self._open_catalog(ROOT_PATH + "/" + self.paths["txt"])
        ))
        self.ui.quick_nav["strs"].clicked.connect(lambda: (
            self._open_catalog(ROOT_PATH + "/" + self.paths["structs"])
        ))
        self.ui.quick_nav["root"].clicked.connect(lambda: (
            self._open_catalog(ROOT_PATH)
        ))

        pass

    def _window_focus_event(self, event):

        if event is None:
            return False

        self._structure_selected_event()

        # reload structures
        structs_hash = self._get_structs_hash()

        if structs_hash != self.structs_hash:
            self.structs_hash = structs_hash
            self.reload_structures()

        # reload client files
        client_dat_hash = self._get_dat_hash()
        client_edf_hash = self._get_edf_hash()
        if client_dat_hash != self.client_dat_hash:
            self.client_dat_hash = client_dat_hash
            self.reload_client_dat()
        if client_edf_hash != self.client_edf_hash:
            self.client_edf_hash = client_edf_hash
            self.reload_client_edf()

        pass

    def _structure_selected_event(self):

        self.ui.clear_browser()
        self.ui.to_dat_disable()
        self.ui.to_txt_disable()
        self.ui.test_structure_disable()

        items = self.ui.structs.selectedItems()

        if len(items) == 1:

            self.ui.test_structure_enable()
            self._structure_selected_single(items[0])

        elif len(items) > 1:

            self.ui.test_structure_enable()
            self._structure_selected_several(items)

        pass

    def _structure_selected_single(self, item):

        structure = self.structures[item.text()]

        if structure.ready_to_dat():
            self.ui.to_dat_enable()
        else:
            self.ui.to_dat_disable()

        if structure.ready_to_txt():
            self.ui.to_txt_enable()
        else:
            self.ui.to_txt_disable()

        self.ui.set_structures_info(structure.get_info())

        pass

    def _structure_selected_several(self, items):

        self.ui.to_dat_enable()
        self.ui.to_txt_enable()

        structures = []
        data = {
            "title": str(len(items)) + " structures selected",
            "note": "",
            "dat_count": 0,
            "txt_count": 0,
            "dat_files": {
                "server": [],
                "client": []
            },
            "txt_files": []
        }

        # get structures instances and structures info
        for item in items:
            structure = self.structures[item.text()]
            info = structure.get_info()
            data["dat_count"] += info["dat_count"]
            data["txt_count"] += info["txt_count"]
            data["dat_files"]["server"].extend(info["dat_files"]["server"])
            data["dat_files"]["client"].extend(info["dat_files"]["client"])
            data["txt_files"].extend(info["txt_files"])
            structures.append(structure)

        # is ready to convert to DAT?
        for structure in structures:
            if not structure.ready_to_dat():
                self.ui.to_dat_disable()
                break

        # is ready to convert to TXT?
        for structure in structures:
            if not structure.ready_to_txt():
                self.ui.to_txt_disable()
                break

        self.ui.set_structures_info(data)

        pass

    def _open_catalog(self, path):

        if os.path.isdir(path):
            os.startfile(path)
        else:
            self.ui.alert_error("Can't find catalog!<br>" + path)

        pass

    def _reset_task(self):

        self.task_type = 0
        self.task_queue = []
        self.task_steps = 0
        self.task_current = 0

        pass

    def _init_dat_file(self, file_name):

        file_path = ROOT_PATH + "/" + self.paths["cli_dat"] + "/" + file_name
        file_instance = DATFile(file_name, file_path, self.paths)
        file_instance.set_callbacks({
            "current_progress": self.emit_current_progress
        })
        self.client_dat_files[file_name] = file_instance

        return file_instance

        pass

    def _init_edf_file(self, file_name):

        file_path = ROOT_PATH + "/" + self.paths["cli_edf"] + "/" + file_name
        file_instance = EDFFile(file_name, file_path, self.paths)
        file_instance.set_callbacks({
            "current_progress": self.emit_current_progress
        })
        self.client_edf_files[file_name] = file_instance

        return file_instance

        pass

    pass
