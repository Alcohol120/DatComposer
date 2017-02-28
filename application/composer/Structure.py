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

        self.structure = OrderedDict()

        self.callback = Callback()

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
            self.callback.assert_error("Cannot find structure data!", "Runtime error!")
            return False

        try:

            self._check_additional_params()
            self._check_required_blocks()
            for name, data in self.structure["dat_structures"].items():
                self._check_structure(name, "dat", data)
            for name, data in self.structure["txt_structures"].items():
                self._check_structure(name, "txt", data)
            for dat_file in self.structure["dat_files"]:
                self._check_dat_file(dat_file)
            for txt_file in self.structure["txt_files"]:
                self._check_txt_files(txt_file)

        except ValueError as error:
            self.callback.assert_error(self.name + " is invalid!<br>" + str(error), "Structure validation failed!")
            return False
        except RuntimeError as error:
            self.callback.assert_error(self.name + " is invalid!<br>" + str(error), "Runtime error!")
            return False

        return True

        pass

    def set_callback(self, callback):

        self.callback.set_callback(callback)

        pass

    # Private Methods

    def _check_additional_params(self):

        if "note" in self.structure and type(self.structure["note"]) is not str:
            error = "'note' attr must contain string value!"
            raise ValueError(error)

        pass

    def _check_required_blocks(self):

        if "dat_structures" not in self.structure:
            error = "'dat_structures' block are required!"
            raise ValueError(error)
        if type(self.structure["dat_structures"]) is not OrderedDict:
            error = "'dat_structures' block must contain a dictionary ({})!"
            raise ValueError(error)
        if len(self.structure["dat_structures"]) < 1:
            error = "'dat_structures' block must contain at least one structure!"
            raise ValueError(error)

        if "txt_structures" not in self.structure:
            error = "'txt_structures' block are required!"
            raise ValueError(error)
        if type(self.structure["txt_structures"]) is not OrderedDict:
            error = "'txt_structures' block must contain a dictionary ({})!"
            raise ValueError(error)
        if len(self.structure["txt_structures"]) < 1:
            error = "'txt_structures' block must contain at least one structure!"
            raise ValueError(error)

        if "dat_files" not in self.structure:
            error = "'dat_files' block are required!"
            raise ValueError(error)
        if type(self.structure["dat_files"]) is not list:
            error = "'dat_files' block must contain a list ([])!"
            raise ValueError(error)
        if len(self.structure["dat_files"]) < 1:
            error = "'dat_files' block must contain at least one file!"
            raise ValueError(error)

        if "txt_files" not in self.structure:
            error = "'txt_files' block are required!"
            raise ValueError(error)
        if type(self.structure["txt_files"]) is not list:
            error = "'txt_files' block must contain a list ([])!"
            raise ValueError(error)
        if len(self.structure["txt_files"]) < 1:
            error = "'txt_files' block must contain at least one file!"
            raise ValueError(error)

        pass

    def _check_structure(self, structure_name, structure_type, structure):

        if structure_type == "dat":
            error_path = "In: dat_structures"
        elif structure_type == "txt":
            error_path = "In: txt_structures"
        else:
            raise RuntimeError("Unknown structure type: '{}'!".format(str(structure_type)))

        if type(structure) is not list:
            error = "'{}' must contain a list ([])!<br>".format(structure_name)
            error += error_path
            raise ValueError(error)
        if len(structure) < 1:
            error = "'{}' must contain at least one field!<br>".format(structure_name)
            error += error_path
            raise ValueError(error)

        # validate structure fields
        for field in structure:
            self._check_field_block(field, structure_name, structure_type)

        pass

    def _check_field_block(self, field, structure_name, structure_type):

        if structure_type == "dat":
            error_path = "In: dat_structures->{}".format(structure_name)
        elif structure_type == "txt":
            error_path = "In: txt_structures->{}".format(structure_name)
        else:
            raise RuntimeError("Unknown structure type: '{}'!".format(str(structure_type)))

        if "repeat" not in field:
            # common field
            if structure_type == "dat":
                self._check_dat_field(field, "dat_structures->" + structure_name)
            else:
                self._check_txt_field(field, structure_name)
        else:
            # repeated section
            if type(field["repeat"]) is int:
                if field["repeat"] < 1:
                    error = "'repeat' attr can't be less than 1!<br>"
                    raise ValueError(error + error_path)
            elif type(field["repeat"]) is not str:
                error = "'repeat' attr must contain int value or string value with valid expression!<br>"
                raise ValueError(error + error_path)

            if "fields" not in field:
                error = "'fields' block is required in repeated section!<br>"
                raise ValueError(error + error_path)
            if type(field["fields"]) is not list or len(field["fields"]) < 1:
                error = "'fields' block must contain a list ([]) with at least one field!<br>"
                raise ValueError(error + error_path)

            for repeated in field["fields"]:
                if structure_type == "dat":
                    self._check_dat_field(repeated, "dat_structures->" + structure_name)
                else:
                    self._check_txt_field(repeated, structure_name)

        pass

    def _check_dat_field(self, field, error_path):

        if "title" not in field or type(field["title"]) is not str:
            error = "'title' attr is required and must contain a string value!<br>"
            error += "In: " + error_path
            raise ValueError(error)

        if "type" not in field or type(field["type"]) is not str:
            error = "'type' attr is required and must contain a string value!<br>"
            error += "In: " + error_path
            raise ValueError(error)
        if not self._check_field_type(field["type"]):
            error = "Invalid 'type' attr! '{}' is incorrect field type!<br>".format(field["type"])
            error += "In: " + error_path + "->{}".format(field["title"] or "Unnamed field")
            raise ValueError(error)
        if field["type"] == "cstr":
            if "len" in field:
                if type(field["len"]) is int and field["len"] < 1:
                    error = "'len' attr can't be less then 1!<br>"
                    error += "In: " + error_path + "->{}".format(field["title"] or "Unnamed field")
                    raise ValueError(error)
                elif type(field["len"]) is not str and type(field["len"]) is not int:
                    error = "'len' attr must contain int or string value!<br>"
                    error += "In: " + error_path + "->{}".format(field["title"] or "Unnamed field")
                    raise ValueError(error)

        if "value" in field and type(field["value"]) is not str:
            error = "'value' attr must contain string value!<br>"
            error += "In: " + error_path + "->{}".format(field["title"] or "Unnamed field")
            raise ValueError(error)

        if "rule" in field and type(field["rule"]) is not str:
            error = "'rule' attr must contain string value!<br>"
            error += "In: " + error_path + "->{}".format(field["title"] or "Unnamed field")
            raise ValueError(error)
        if "rule" in field and getattr(rules, field["rule"], None) is None:
            error = "Unknown rule '{}'!<br>".format(field["rule"])
            error += "In: " + error_path + "->{}".format(field["title"] or "Unnamed field")
            raise ValueError(error)

        if "use" in field and type(field["use"]) is not str:
            error = "'use' attr must contain string value!<br>"
            error += "In: " + error_path + "->{}".format(field["title"] or "Unnamed field")
            raise ValueError(error)

        pass

    @staticmethod
    def _check_txt_field(field, structure_name):

        if "title" not in field or type(field["title"]) is not str:
            error = "'title' attr is required and must contain a string value!<br>"
            error += "In: txt_structures->{}".format(structure_name)
            raise ValueError(error)

        if "from" not in field or type(field["from"]) is not str:
            error = "'from' attr is required and must contain a string value!<br>"
            error += "In: txt_structures->{}".format(structure_name)
            raise ValueError(error)

        if "field" not in field or type(field["field"]) is not str:
            error = "'field' attr is required and must contain a string value!<br>"
            error += "In: txt_structures->{}".format(structure_name)
            raise ValueError(error)

        pass

    def _check_dat_file(self, file):

        if "side" not in file or type(file["side"]) is not str:
            error = "'side' attr is required and must contain a string value!<br>"
            error += "In: dat_files"
            raise ValueError(error)
        if file["side"] != "server" and file["side"] != "client":
            error = "Invalid 'side' attr! Available values is 'client' or 'server'!<br>"
            error += "In: dat_files"
            raise ValueError(error)

        if "source_file" not in file or type(file["source_file"]) is not str:
            error = "'source_file' attr is required and must contain a string value!<br>"
            error += "In: dat_files"
            raise ValueError(error)
        if re.search(FILE_PATH_EXT_RE("dat"), file["source_file"]) is None:
            error = "'source_file' attr must contain a valid path to DAT-file!<br>"
            error += "In: dat_files"
            raise ValueError(error)

        if "header_file" not in file or type(file["header_file"]) is not str:
            error = "'header_file' attr is required and must contain a string value!<br>"
            error += "In: dat_files"
            raise ValueError(error)
        if re.search(FILE_PATH_EXT_RE("json"), file["header_file"]) is None:
            error = "'header_file' attr must contain a valid path to JSON-file!<br>"
            error += "In: dat_files"
            raise ValueError(error)

        if "groups" not in file or type(file["groups"]) is not list:
            error = "'groups' attr is required and must contain a list ([])!<br>"
            error += "In: dat_files"
            raise ValueError(error)
        if len(file["groups"]) < 1:
            error = "'groups' attr must contain at least one group!<br>"
            error += "In: dat_files"
            raise ValueError(error)

        # validate file groups
        for group in file["groups"]:
            self._check_file_group(group)

        pass

    def _check_file_group(self, group):

        if "group_name" not in group or type(group["group_name"]) is not str:
            error = "'group_name' attr is required and must contain a string value!<br>"
            error += "In: dat_files->groups"
            raise ValueError(error)

        if "count" not in group:
            error = "'count' attr is required!<br>"
            error += "In: dat_files->groups->{}".format(group["group_name"])
            raise ValueError(error)
        if type(group["count"]) is not int and type(group["count"]) is not str:
            error = "'count' attr must contain string or int value!<br>"
            error += "In: dat_files->groups->{}".format(group["group_name"])
            raise ValueError(error)
        if type(group["count"]) is int and group["count"] < 1:
            error = "'count' attr can't be less than 1!<br>"
            error += "In: dat_files->groups->{}".format(group["group_name"])
            raise ValueError(error)

        if "count_override" in group and type(group["count"]) is not str:
            error = "'count_override' attr must contain string value!<br>"
            error += "In: dat_files->groups->{}".format(group["group_name"])
            raise ValueError(error)

        if "structure" not in group or type(group["structure"]) is not str:
            error = "'structure' attr is required and must contain a string value!<br>"
            error += "In: dat_files->groups->{}".format(group["group_name"])
            raise ValueError(error)

        # validate 'header' block
        if "header" in group:
            if type(group["header"]) is not list:
                error = "'header' attr must contain a list ([])!<br>"
                error += "In: dat_files->groups->{}".format(group["group_name"])
                raise ValueError(error)
            for field in group["header"]:
                error_path = "dat_files->groups->{}->header".format(group["group_name"])
                self._check_dat_field(field, error_path)

        pass

    @staticmethod
    def _check_txt_files(file):

        if "output_file" not in file or type(file["output_file"]) is not str:
            error = "'output_file' attr is required and must contain a string value!<br>"
            error += "In: txt_files"
            raise ValueError(error)
        if re.search(FILE_PATH_EXT_RE("txt"), file["output_file"]) is None:
            error = "'output_file' attr must contain a valid path to TXT-file!<br>"
            error += "In: txt_files"
            raise ValueError(error)

        if "groups" not in file or type(file["output_file"]) is not str:
            error = "'groups' attr is required and must contain a string value!<br>"
            error += "In: txt_files"
            raise ValueError(error)

        if "structure" not in file or type(file["output_file"]) is not str:
            error = "'structure' attr is required and must contain a string value!<br>"
            error += "In: txt_files"
            raise ValueError(error)

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
