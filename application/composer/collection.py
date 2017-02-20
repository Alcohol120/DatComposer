from application.config import *
import os


class Collection:

    def __init__(self, data):

        self.name = data["name"]
        self.paths = data["paths"]

        self.prepare_catalogs()

        pass

    def prepare_catalogs(self):

        if not self._check_catalogs():
            self._create_catalogs()

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
                os.makedirs(ROOT_PATH + "/" + path)

        pass

    pass
