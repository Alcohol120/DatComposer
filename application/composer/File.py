from application.config import *
import os


class File:

    def __init__(self, file_name, file_path):

        self.file_name = file_name
        self.file_path = file_path

        pass

    def get_name(self):

        return self.file_name

        pass

    def is_exists(self):

        if os.path.isfile(self.file_path):
            return True
        else:
            return False

        pass

    def _read(self):

        try:
            file = open(self.file_path, "r")
            structure = file.read()
            file.close()
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
