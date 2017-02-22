from application.config import *
from application.composer.Callback import Callback
from application.composer.Rules import rules
import os
import re
import json
from collections import OrderedDict


class Structure:

    def __init__(self, file_name, location):

        self.name = file_name.replace(".json", "")
        self.file_name = file_name
        self.file_path = location + "/" + file_name
        self.location = location

        self.structure = OrderedDict()

        self.callback = Callback()

        self._last_error = ""

        pass

    def omg(self):

        return False

        pass

    def get_name(self):

        return self.name

        pass

    def load(self):

        if not self._read_structure_file():
            return False

        return True

        pass

    def validate(self):

        if not self.structure:
            return False

        try:

            if not self.check_additional_params():
                raise ValueError(self.get_error())
            if not self.check_required_blocks():
                raise ValueError(self.get_error())
            if not self.check_dat_structures():
                raise ValueError(self.get_error())

        except ValueError:
            self.callback.assert_error(self.get_error(), "Invalid structure")
            return False

        return True

        pass

    def check_additional_params(self):

        if "note" in self.structure and type(self.structure["note"]) is not str:
            self._last_error = "'note' must contain string value!"
            return False

        return True

        pass

    def check_required_blocks(self):

        if "dat_structures" not in self.structure:
            self._last_error = "'dat_structures' block are required!"
            return False
        if type(self.structure["dat_structures"]) is not OrderedDict:
            self._last_error = "'dat_structures' block must contain a dictionary ({})!"
            return False
        if len(self.structure["dat_structures"]) < 1:
            self._last_error = "'dat_structures' block is empty!"
            return False

        if "txt_structures" not in self.structure:
            self._last_error = "'txt_structures' block are required!"
            return False
        if type(self.structure["txt_structures"]) is not OrderedDict:
            self._last_error = "'txt_structures' block must contain a dictionary ({})!"
            return False
        if len(self.structure["txt_structures"]) < 1:
            self._last_error = "'txt_structures' block is empty!"
            return False

        if "dat_files" not in self.structure:
            self._last_error = "'dat_files' block are required!"
            return False
        if type(self.structure["dat_files"]) is not list:
            self._last_error = "'dat_files' block must contain a list ([])!"
            return False
        if len(self.structure["dat_files"]) < 1:
            self._last_error = "'dat_files' block is empty!"
            return False

        if "txt_files" not in self.structure:
            self._last_error = "'txt_files' block are required!"
            return False
        if type(self.structure["txt_files"]) is not list:
            self._last_error = "'txt_files' block must contain a list ([])!"
            return False
        if len(self.structure["txt_files"]) < 1:
            self._last_error = "'txt_files' block is empty!"
            return False

        return True

        pass

    def check_dat_structures(self):

        for name, data in self.structure["dat_structures"].items():
            if type(self.structure["dat_structures"][name]) is not list:
                self._last_error = "DATStructure '{}' must contain a list ([])!".format(name)
                return False
            if len(self.structure["dat_structures"][name]) < 1:
                self._last_error = "DATStructure '{}' is empty!".format(name)
                return False

            for field in data:
                # check repeat
                if "repeat" in field:
                    if type(field["repeat"]) is not int or field["repeat"] < 1:
                        self._last_error = "'repeat' attr must contain int value, over 1!<br>"
                        self._last_error += "dat_structures->{}".format(name)
                        return False
                    if "fields" not in field:
                        self._last_error = "'fields' block is required in repeated section!<br>"
                        self._last_error += "dat_structures->{}".format(name)
                        return False
                    if type(field["fields"]) is not list or len(field["fields"]) < 1:
                        self._last_error = "'fields' block must contain a list ([]) and can't be empty!<br>"
                        self._last_error += "dat_structures->{}".format(name)
                        return False

                    for repeated in field["fields"]:
                        if not self._check_dat_field(repeated, name):
                            return False
                else:
                    # common fields
                    if not self._check_dat_field(field, name):
                        return False

        return True

        pass

    def get_error(self):

        return self._last_error

        pass

    def set_callback(self, callback):

        self.callback.set_callback(callback)

        pass

    # Private Methods

    def _check_dat_field(self, field, structure_name):

        if "title" not in field or type(field["title"]) is not str:
            self._last_error = "'title' attr is required and must contain a string value!<br>"
            self._last_error += "dat_structures->{}".format(structure_name)
            return False

        if "type" not in field or type(field["type"]) is not str:
            self._last_error = "'type' attr is required and must contain a string value!<br>"
            self._last_error += "dat_structures->{}".format(structure_name)
            return False
        if not self._check_field_type(field["type"]):
            self._last_error = "Invalid 'type' attr! '{}' is incorrect field type!<br>".format(field["type"])
            self._last_error += "dat_structures->{}->{}".format(structure_name, field["title"] or "Unnamed")
            return False
        if field["type"] == "cstr":
            if "len" in field:
                if type(field["len"]) is int and field["len"] < 1:
                    self._last_error = "'len' attr can't be less then 1!<br>"
                    self._last_error += "dat_structures->{}->{}".format(structure_name, field["title"] or "Unnamed")
                    return False
                elif type(field["len"]) is not str and type(field["len"]) is not int:
                    self._last_error = "'len' attr must contain int or string value!<br>"
                    self._last_error += "dat_structures->{}->{}".format(structure_name, field["title"] or "Unnamed")
                    return False

        if "value" in field and type(field["value"]) is not str:
            self._last_error = "'value' attr must contain string value!<br>"
            self._last_error += "dat_structures->{}->{}".format(structure_name, field["title"] or "Unnamed")
            return False

        if "rule" in field and type(field["rule"]) is not str:
            self._last_error = "'rule' attr must contain string value!<br>"
            self._last_error += "dat_structures->{}->{}".format(structure_name, field["title"] or "Unnamed")
            return False
        if "rule" in field and getattr(rules, field["rule"], None) is None:
            self._last_error = "Unknown rule '{}'!<br>".format(field["rule"])
            self._last_error += "dat_structures->{}->{}".format(structure_name, field["title"] or "Unnamed")
            return False

        if "use" in field and type(field["use"]) is not str:
            self._last_error = "'rule' attr must contain string value!<br>"
            self._last_error += "dat_structures->{}->{}".format(structure_name, field["title"] or "Unnamed")
            return False

        return True

        pass

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

    @staticmethod
    def _check_field_type(f_type):

        if f_type == "i8":
            return True
        elif f_type == "i16":
            return True
        elif f_type == "i32":
            return True
        elif f_type == "u8":
            return True
        elif f_type == "u16":
            return True
        elif f_type == "u32":
            return True
        elif f_type == "x8":
            return True
        elif f_type == "x16":
            return True
        elif f_type == "x32":
            return True
        elif f_type == "float":
            return True
        elif f_type == "double":
            return True
        elif f_type == "cstr":
            return True

        return False

        pass

    pass
