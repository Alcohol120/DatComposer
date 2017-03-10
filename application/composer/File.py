from application.config import *
import os


class File:

    def __init__(self, file_name, file_path):

        self.file_name = file_name
        self.file_path = file_path

        self.source = ""

        self.callbacks = {
            "current_progress": self._callback_dummy,
            "current_progress_text": self._callback_dummy,
            "step_completed": self._callback_dummy
        }

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

    def set_callbacks(self, callbacks):

        if "current_progress" in callbacks:
            self.callbacks["current_progress"] = callbacks["current_progress"]

        if "current_progress_text" in callbacks:
            self.callbacks["current_progress_text"] = callbacks["current_progress_text"]

        if "step_completed" in callbacks:
            self.callbacks["step_completed"] = callbacks["step_completed"]

        pass

    def read(self):

        try:
            file = open(self.file_path, "rb")
            data = file.read()
            file.close()
        except FileNotFoundError:
            return False
        except PermissionError:
            return False
        except ValueError:
            return False

        self.source = data

        return True

        pass

    # Private Methods

    @staticmethod
    def _callback_dummy(*values):

        print("File Class: %s" % list(values))

        pass

    pass
