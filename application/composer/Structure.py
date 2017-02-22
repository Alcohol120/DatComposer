from application.config import *
import os
import json
from collections import OrderedDict


class Structure:

    def __init__(self, file_name, location):

        self.file_name = file_name
        self.file_path = location + "/" + file_name
        self.location = location

        self.structure = OrderedDict()

        pass

    def load(self):

        if not self._read_structure_file():
            return False

        if not self.validate():
            return False

        return True

        pass

    def validate(self):

        if not self.structure:
            return False

        return True

        pass

    # Private Methods

    def _read_structure_file(self):

        try:
            file = open(self.file_path, "r")
            structure = file.read()
            file.close()
            structure = json.loads(structure, object_pairs_hook=OrderedDict)
        except FileNotFoundError:
            return False
        except PermissionError:
            return False
        except ValueError:
            return False

        self.structure = structure

        return True

        pass

    pass
