from application.config import *
from application.interface.gui import GUI
from application.interface.events import Events
from application.composer.collection import Collection
import os
import re
import sys
import json


class Core:

    collections = []
    active = ""

    def init_app(self):

        ui = GUI()
        app = ui.setup(sys.argv)

        # load collections config file
        collections = self.load_collections()
        if not collections:
            ui.alert_error("Can't load collections config file!<br>{}/config/collections.json!".format(ROOT_PATH))
            self.quit()

        # setup workspace for each collection
        # initialize collections objects
        for collection in collections:
            if self.active == "":
                # set first collection to active workspace
                self.active = collection["name"]
            self.collections.append(Collection(collection))
            ui.setup_workspace(collection)
            Events(collection["name"])

        sys.exit(app.exec())

        pass

    def load_collections(self):

        collections = self._load_collections_config()

        if self._validate_collections_config(collections):
            return collections
        else:
            return False

        pass

    @staticmethod
    def quit():

        sys.exit()

        pass

    def _load_collections_config(self):

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

    def _validate_collections_config(self, collections):

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

core = Core()
