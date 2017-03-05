from application.config import *
from application.interface.Layout import Layout
from application.composer.Collection import Collection
import re
import sys
import json
import ctypes
import platform


class Core:

    def __init__(self):

        self.layout = Layout()
        self.collections = []

        # set Windows AppID
        if platform.system() == "Windows":
            app_id = "AlcLab." + APP_NAME + "." + APP_NAME + "." + APP_VERSION
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        pass

    def run(self):

        self._init_app()

        # load collections config file
        collections = self.load_collections()
        if not collections:
            message = "Can't load collections config file!<br>{}/config/collections.json!".format(ROOT_PATH)
            self.layout.alert_error(message)
            sys.exit()

        # setup collections
        for collection in collections:
            self.setup_collection(collection)

        # register events
        self._register_events()

        app = self.layout.get_app_instance()
        sys.exit(app.exec())

        pass

    def load_collections(self):

        collections = self._load_collections_config()

        if self._validate_collections_config(collections):
            return collections
        else:
            return False

        pass

    def setup_collection(self, collection):

        self.collections.append(Collection(collection))

        pass

    # Private Methods

    def _init_app(self):

        self.layout = Layout()
        self.layout.setup(sys.argv)

        pass

    @staticmethod
    def _load_collections_config():

        try:
            file = open(ROOT_PATH + "/config/collections.json", "r")
            collections = file.read()
            file.close()
            collections = json.loads(collections)
        except FileNotFoundError:
            return False
        except PermissionError:
            return False
        except ValueError:
            return False

        return collections

        pass

    @staticmethod
    def _validate_collections_config(collections):

        if type(collections) is not list:
            return False
        for collection in collections:
            if "name" not in collection:
                return False
            if re.search("^[a-zA-Z0-9_\-. ()]+$", collection["name"]) is None:
                return False

            if "paths" not in collection or type(collection["paths"])  is not dict:
                return False
            path_cfg = collection["paths"]
            if "structs" not in path_cfg or re.search(DIR_NAME_RE, path_cfg["structs"]) is None:
                return False
            if "txt" not in path_cfg or re.search(DIR_NAME_RE, path_cfg["txt"]) is None:
                return False
            if "srv_dat" not in path_cfg or re.search(DIR_NAME_RE, path_cfg["srv_dat"]) is None:
                return False
            if "cli_dat" not in path_cfg or re.search(DIR_NAME_RE, path_cfg["cli_dat"]) is None:
                return False
            if "cli_edf" not in path_cfg or re.search(DIR_NAME_RE, path_cfg["cli_edf"]) is None:
                return False

        return True

        pass

    def _register_events(self):

        self.layout.menu_bar_items["File"]["Quit"].triggered.connect(sys.exit)
        self.layout.menu_bar_items["File"]["Test Structure"].triggered.connect(self._validate_structure_event)
        self.layout.tabs.currentChanged.connect(self._tab_changed_event)

        pass

    def _validate_structure_event(self):

        active_collection = self.layout.tabs.currentIndex()

        self.collections[active_collection].validate_selected_structures()

        pass

    def _tab_changed_event(self):

        self.layout.menu_bar_items["File"]["Convert to TXT"].setEnabled(0)
        self.layout.menu_bar_items["File"]["Convert to DAT"].setEnabled(0)
        self.layout.menu_bar_items["File"]["Test Structure"].setEnabled(0)

        for collection in self.collections:
            collection.reset_user_actions()

        pass

core = Core()
