from application.config import *
from application.interface.Workspace import Workspace
from application.composer.Structure import Structure
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
        self.structs_hash = self._get_hash()

        # tasks
        self.task_active = False
        self.task_queue = []
        self.task_steps = 0

        self.prepare_catalogs()
        self.ui.setup_workspace()

        self.reload_structures()

        self._register_events()

        pass

    def prepare_catalogs(self):

        if not self._check_catalogs():
            self._create_catalogs()

        pass

    def reload_structures(self):

        self.ui.clear_structs_list()

        if not self._check_catalog("structs"):
            return []

        files = self._get_structure_files()

        for file in files:
            structure = Structure(file, self.paths)
            structure.set_callback(self)
            if structure.load():
                self.structures[file.replace(".json", "")] = structure
                self.ui.add_structure(structure.get_name())
            else:
                del structure

        pass

    def validate_selected_structures(self):

        items = self.ui.structs.selectedItems()

        if len(items) == 1:
            self.structures[items[0].text()].validate()
        elif len(items) > 1:
            result = []
            for item in items:
                structure = self.structures[item.text()]
                test = structure.validate_quietly()
                test["name"] = structure.get_name()
                result.append(test)

            self.ui.structures_test_result(result)

        pass

    def convert_to_dat(self):

        pass

    def convert_to_txt(self):

        items = self.ui.structs.selectedItems()
        self.task_queue = []
        self.task_steps = 0

        if len(items) > 0:

            print("Start converting to TXT {} structures!".format(str(len(items))))

            # validate structures
            for item in items:
                test_result = self.structures[item.text()].validate_quietly()
                if not test_result["success"]:
                    error = "<p><span style='color: red;'>{}</span></p>".format(test_result["title"])
                    error += test_result["error_message"]
                    self.assert_error(error, test_result["error_type"])
                    return False

            # prepare task
            for item in items:
                struct = self.structures[item.text()]
                self.task_steps += struct.get_steps_count()
                thread = threading.Thread(target=struct.to_txt)
                thread.setDaemon(True)
                self.task_queue.append(thread)

            # show progress bar
            self.ui.show_progress()

            # start task
            thread = threading.Thread(target=self._start_tasks)
            thread.setDaemon(True)
            thread.start()

            return True

        pass

    def _start_tasks(self):

        start_time = time.time()

        for index, task in enumerate(self.task_queue):
            print("Task #{} started!".format(index))
            task.start()
            while task.isAlive():
                continue
            print("Task #{} completed!".format(index))

        working_time = math.floor(time.time() - start_time)
        working_time = datetime.timedelta(seconds=working_time)
        print("Converting complete by: {}".format(working_time))

        pass

    def assert_error(self, message, title=""):

        if title != "":
            self.ui.alert_error(message, title)
        else:
            self.ui.alert_error(message)

        pass

    def assert_success(self, message, title=""):

        if title != "":
            self.ui.alert_success(message, title)
        else:
            self.ui.alert_success(message)

        pass

    def reset_user_actions(self):

        self.ui.clear_browser()
        self.ui.deselect_encoder_list()
        self.ui.deselect_decoder_list()
        self.ui.deselect_structures_list()

        pass

    # Private Methods

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
                    self.assert_error("Can't create collection catalogs!", "Filesystem error!")

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

    def _get_hash(self):

        if not self._check_catalog("structs"):
            return []

        structs_path = ROOT_PATH + "/" + self.paths["structs"]

        files = self._get_structure_files()

        times = ""

        for file in files:
            times += str(os.path.getmtime(structs_path + "/" + file))

        if times == "":
            return False

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
            return

        if self.task_active:
            return

        print("RELOADING")

        structs_hash = self._get_hash()

        if structs_hash != self.structs_hash:
            self.structs_hash = structs_hash
            self.reload_structures()

        pass

    def _structure_selected_event(self):

        self.ui.clear_browser()
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

        self.ui.to_dat_disable()
        self.ui.to_txt_disable()

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

    pass
