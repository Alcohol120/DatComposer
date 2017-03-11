from application.config import *
import os


class File:

    def __init__(self, file_name, file_path, paths):

        self.file_name = file_name
        self.file_path = file_path
        self.paths = paths

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

    def get_path(self):

        return self.file_path

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

    # Private Methods

    @staticmethod
    def _callback_dummy(*values):

        print("File Class: %s" % list(values))

        pass

    pass
