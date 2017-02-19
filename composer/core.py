from composer.config import *
from composer.interface.gui import GUI
import os
import re
import sys
import json


class Core:

    app = object
    collections = list

    def init_app(self):

        ui = GUI()
        self.app = ui.setup(sys.argv)

        self.reload_collections()

        sys.exit(self.app.exec())

        pass

    def reload_collections(self):

        # read collections file
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

        # validate collections file
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

        self.collections = collections
        return True

        pass

core = Core()
