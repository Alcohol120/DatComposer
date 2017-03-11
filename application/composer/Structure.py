from application.config import *
from application.composer.Rules import rules
from application.composer.DATFile import DATFile
from application.composer.TXTFile import TXTFile
import re
import json
import copy


class Structure:

    def __init__(self, file_name, paths):

        self.name = file_name.replace(".json", "")
        self.file_name = file_name
        self.file_path = ROOT_PATH + "/" + paths["structs"] + "/" + file_name
        self.paths = paths

        self.structure = {}

        self.dat_files = []
        self.txt_files = []

        self.callbacks = {
            "alert_error": self._callback_dummy,
            "current_progress": self._callback_dummy,
            "total_progress": self._callback_dummy,
            "current_progress_text": self._callback_dummy
        }

        self.total_steps = 0
        self.current_step = 0

        pass

    def get_name(self):

        return self.name

        pass

    def set_callbacks(self, callbacks):

        if "alert_error" in callbacks:
            self.callbacks["alert_error"] = callbacks["alert_error"]

        if "current_progress" in callbacks:
            self.callbacks["current_progress"] = callbacks["current_progress"]

        if "total_progress" in callbacks:
            self.callbacks["total_progress"] = callbacks["total_progress"]

        if "current_progress_text" in callbacks:
            self.callbacks["current_progress_text"] = callbacks["current_progress_text"]

        pass

    def load(self):

        # try to read structure file
        if not self._read_structure_file():
            return False

        # check general structure blocks
        try:
            self._check_required_blocks()
        except ValueError:
            return False

        # init file objects
        for file in self.structure["dat_files"]:
            # check required parameters
            if "side" not in file or (file["side"] != "server" and file["side"] != "client"):
                continue
            if "source_file" not in file or re.search(FILE_PATH_EXT_RE("dat"), file["source_file"]) is None:
                continue
            self._init_dat_file(file)

        for file in self.structure["txt_files"]:
            # check required parameters
            if "output_file" not in file or re.search(FILE_PATH_EXT_RE("txt"), file["output_file"]) is None:
                continue
            self._init_txt_file(file)

        return True

        pass

    def validate(self):

        if not self.structure:
            return {
                "success": False,
                "error_type": "Runtime error!",
                "error_message": "Cannot find structure data!"
            }

        try:

            # validate general blocks
            self._check_required_blocks()
            # validate structures
            for name, data in self.structure["dat_structures"].items():
                self._check_structure(name, "dat", data)
            for name, data in self.structure["txt_structures"].items():
                self._check_structure(name, "txt", data)
            # validate files
            for dat_file in self.structure["dat_files"]:
                self._check_dat_file(dat_file)
            for txt_file in self.structure["txt_files"]:
                self._check_txt_files(txt_file)
            # check dat headers
            self._check_file_headers()
            self._check_file_names()
            # check usage
            self._check_structures_usage()
            self._check_groups_usage()
            # check fields linking
            self._check_fields_linking()

        except ValueError as error:
            return {
                "success": False,
                "title": self.name + " is invalid!",
                "error_type": "Structure validation failed!",
                "error_message": str(error)
            }
        except RuntimeError as error:
            return {
                "success": False,
                "title": self.name + " is invalid!",
                "error_type": "Runtime error!",
                "error_message": str(error)
            }

        return {
            "success": True,
            "title": self.name + " is valid!"
        }

        pass

    def ready_to_txt(self):

        for file in self.dat_files:
            if not file.is_exists():
                return False

        return True

        pass

    def ready_to_dat(self):

        for file in self.txt_files:
            if not file.is_exists():
                return False

        return True

        pass

    def get_info(self):

        data = {
            "title": self.name,
            "note": "",
            "dat_count": len(self.structure["dat_files"]),
            "txt_count": len(self.structure["txt_files"]),
            "dat_files": {
                "server": [],
                "client": []
            },
            "txt_files": []
        }

        if "note" in self.structure and type(self.structure["note"]) is str:
            data["note"] = self.structure["note"]
        else:
            data["note"] = ""

        for file in self.dat_files:
            data["dat_files"][file.get_side()].append({
                "name": file.get_name(),
                "exists": file.is_exists()
            })

        for file in self.txt_files:
            data["txt_files"].append({
                "name": self.name + "/" + file.get_name(),
                "exists": file.is_exists()
            })

        return data

        pass

    def get_steps_to_txt(self):

        total = len(self.structure["txt_files"]) * 2
        for file in self.structure["dat_files"]:
            total += len(file["groups"])

        return total

        pass

    def get_steps_to_dat(self):

        total = len(self.structure["txt_files"])
        for file in self.structure["dat_files"]:
            total += len(file["groups"]) * 2

        return total

        pass

    def to_dat(self):

        self.total_steps = self.get_steps_to_dat()
        self.current_step = 0

        # reading TXT files
        read_result = self._read_txt_files()
        if not read_result["success"]:
            for file in self.txt_files:
                file.reset()
            return read_result
        else:
            txt_data = read_result["txt_data"]

        # build DAT files
        build_result = self._build_dat_files(txt_data)
        if not build_result["success"]:
            build_result["title"] = "Composing error!"
            for file in self.txt_files:
                file.reset()
            for file in self.dat_files:
                file.reset()
            return build_result

        for file in self.txt_files:
            file.reset()

        # writing files
        for file in self.dat_files:
            res = file.save()
            file.reset()
            if not res["success"]:
                res["title"] = file.get_name() + "Writing error!"
                for dat in self.dat_files:
                    dat.reset()
                return res

        return {"success": True}

        pass

    def to_txt(self):

        self.total_steps = self.get_steps_to_txt()
        self.current_step = 0

        # reading DAT files
        read_result = self._read_dat_files()
        if not read_result["success"]:
            for file in self.dat_files:
                file.reset()
            return read_result
        else:
            dat_data = read_result["dat_data"]

        # build TXT files
        build_result = self._build_txt_files(dat_data)
        if not build_result["success"]:
            build_result["title"] = "Composing error!"
            for file in self.txt_files:
                file.reset()
            for file in self.dat_files:
                file.reset()
            return build_result

        # writing files
        for file in self.dat_files:
            res = file.save_meta()
            file.reset()
            if not res:
                return {
                    "success": False,
                    "error": "Can't save meta data in header file!",
                    "title": file.get_name() + " writing error!"
                }
        for file in self.txt_files:
            res = file.save()
            file.reset()
            if not res:
                return {
                    "success": False,
                    "error": "Can't save TXT file!<br>{}".format(file.get_path()),
                    "title": file.get_name() + " writing error!"
                }

        return {"success": True}

        pass

    def step_completed(self):

        self.current_step += 1
        self.callbacks["current_progress"](0)
        self.callbacks["total_progress"](self.current_step / (self.total_steps / 100))

        pass

    # Private Methods

    def _init_dat_file(self, file):

        file_data = copy.deepcopy(file)

        # get file path
        file_path = ROOT_PATH + "/"
        if file["side"] == "server":
            file_path += self.paths["srv_dat"] + "/" + file["source_file"]
        else:
            file_path += self.paths["cli_dat"] + "/" + file["source_file"]

        # add catalog name
        file_data["catalog_name"] = self.name

        # replace structure
        for group in file_data["groups"]:
            if group["structure"] in self.structure["dat_structures"]:
                struct = self.structure["dat_structures"][group["structure"]]
                group["structure"] = self._get_structure_fields_map(struct)
            else:
                group["structure"] = False

        # init object
        file_instance = DATFile(file["source_file"], file_path, self.paths, file_data)
        file_instance.set_callbacks({
            "current_progress": self.callbacks["current_progress"],
            "current_progress_text": self.callbacks["current_progress_text"],
            "step_completed": self.step_completed
        })
        self.dat_files.append(file_instance)

        pass

    def _init_txt_file(self, file):

        file_data = copy.deepcopy(file)

        file_path = ROOT_PATH + "/" + self.paths["txt"] + "/" + self.name + "/" + file["output_file"]

        # add catalog name
        file_data["catalog_name"] = self.name

        # replace structure
        if file_data["structure"] in self.structure["txt_structures"]:
            struct = self.structure["txt_structures"][file_data["structure"]]
            file_data["structure"] = self._get_structure_fields_map(struct)
        else:
            file_data["structure"] = False

        # init object
        file_instance = TXTFile(file["output_file"], file_path, self.paths, file_data)
        file_instance.set_callbacks({
            "current_progress": self.callbacks["current_progress"],
            "current_progress_text": self.callbacks["current_progress_text"],
            "step_completed": self.step_completed
        })
        self.txt_files.append(file_instance)

        pass

    def _read_txt_files(self):

        txt_data = {}
        for file in self.txt_files:
            if not file.read():
                return {
                    "success": False,
                    "error": "Can't read file!",
                    "title": file.get_name() + " reading error!"
                }
            result = file.parse()
            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"],
                    "title": file.get_name() + " reading error!"
                }
            else:
                txt_data[file.get_name()] = result["data"]

        return {
            "success": True,
            "txt_data": txt_data
        }

        pass

    def _read_dat_files(self):

        dat_data = {}
        for file in self.dat_files:
            if not file.read():
                return {
                    "success": False,
                    "error": "Can't read file!",
                    "title": file.get_name() + " reading error!"
                }
            result = file.parse()
            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"],
                    "title": file.get_name() + " reading error!"
                }
            else:
                dat_data.update(result["data"])

        return {
            "success": True,
            "dat_data": dat_data
        }

        pass

    def _build_txt_files(self, dat_data):

        for file in self.txt_files:
            needle_groups = file.get_needle_groups()
            fields_map = {}
            for group in needle_groups:
                # dat fields map
                struct = self._get_dat_group_structure(group)
                fields_map[group] = self._get_structure_fields_map(struct)

            file.set_dat_fields_map(fields_map)
            result = file.build(dat_data)
            if not result["success"]:
                result["title"] = file.get_name() + " composing error!"
                return result

        return {"success": True}

        pass

    def _build_dat_files(self, txt_data):

        # get groups map
        groups_map = {}
        for file in self.txt_files:
            groups = file.get_needle_groups()
            for group in groups:
                groups_map[group] = {
                    "file": file.get_name(),
                    "map": file.get_fields_map()
                }

        # build DAT files
        for file in self.dat_files:
            if not file.load_meta():
                return {
                    "success": False,
                    "error": "Can't load header file!",
                    "title": file.get_name() + " composing error!"
                }
            result = file.build(txt_data, groups_map)
            if not result["success"]:
                result["title"] = file.get_name() + " composing error!"
                return result

        return {"success": True}

        pass

    def _get_dat_group_structure(self, name):

        for dat_files in self.structure["dat_files"]:
            for group in dat_files["groups"]:
                if group["group_name"] == name:
                    return self.structure["dat_structures"][group["structure"]]

        return False

        pass

    def _check_required_blocks(self):

        if "dat_structures" not in self.structure:
            error = "'dat_structures' block are required!"
            raise ValueError(error)
        if type(self.structure["dat_structures"]) is not dict:
            error = "'dat_structures' block must contain a dictionary ({})!"
            raise ValueError(error)
        if len(self.structure["dat_structures"]) < 1:
            error = "'dat_structures' block must contain at least one structure!"
            raise ValueError(error)

        if "txt_structures" not in self.structure:
            error = "'txt_structures' block are required!"
            raise ValueError(error)
        if type(self.structure["txt_structures"]) is not dict:
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

        return True

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

        return True

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
            if type(field["repeat"]) is not int or field["repeat"] < 1:
                error = "'repeat' attr must contain a int value and can't be less than 1!<br>"
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

        return True

        pass

    def _check_dat_field(self, field, error_path):

        if "title" not in field or type(field["title"]) is not str or field["title"] == "":
            error = "'title' attr is required and must contain a string value!<br>"
            error += "In: " + error_path
            raise ValueError(error)

        if "type" not in field or type(field["type"]) is not str or field["type"] == "":
            error = "'type' attr is required and must contain a string value!<br>"
            error += "In: " + error_path
            raise ValueError(error)
        if not self._check_field_type(field["type"]):
            error = "Invalid 'type' attr! '{}' is incorrect field type!<br>".format(field["type"])
            error += "In: " + error_path + "->{}".format(field["title"])
            raise ValueError(error)
        if field["type"] == "cstr":
            if "len" in field:
                if type(field["len"]) is int:
                    if field["len"] < 1:
                        error = "'len' attr can't be less then 1!<br>"
                        error += "In: " + error_path + "->{}".format(field["title"])
                        raise ValueError(error)
                elif type(field["len"]) is str:
                    if re.search("^\{(.*?)\}$", field["len"]) is None:
                        error = "'len' attr contains a wrong expression: '{}'!<br>".format(field["len"])
                        error += "In: " + error_path + "->{}".format(field["title"])
                        raise ValueError(error)
                else:
                    error = "'len' attr must contain int or string value!<br>"
                    error += "In: " + error_path + "->{}".format(field["title"])
                    raise ValueError(error)

        if "value" in field and type(field["value"]) is not str:
            error = "'value' attr must contain string value!<br>"
            error += "In: " + error_path + "->{}".format(field["title"])
            raise ValueError(error)

        if "rule" in field and (type(field["rule"]) is not str or field["rule"] == ""):
            error = "'rule' attr must contain string value!<br>"
            error += "In: " + error_path + "->{}".format(field["title"])
            raise ValueError(error)
        if "rule" in field and getattr(rules, field["rule"], None) is None:
            error = "Unknown rule '{}'!<br>".format(field["rule"])
            error += "In: " + error_path + "->{}".format(field["title"])
            raise ValueError(error)

        if "use" in field and (type(field["use"]) is not str or field["use"] == ""):
            error = "'use' attr must contain string value!<br>"
            error += "In: " + error_path + "->{}".format(field["title"])
            raise ValueError(error)

        return True

        pass

    @staticmethod
    def _check_txt_field(field, structure_name):

        if "title" not in field or type(field["title"]) is not str or field["title"] == "":
            error = "'title' attr is required and must contain a string value!<br>"
            error += "In: txt_structures->{}".format(structure_name)
            raise ValueError(error)

        if "from" not in field or type(field["from"]) is not str or field["from"] == "":
            error = "'from' attr is required and must contain a string value!<br>"
            error += "In: txt_structures->{}".format(structure_name)
            raise ValueError(error)

        if "field" not in field or type(field["field"]) is not str or field["field"] == "":
            error = "'field' attr is required and must contain a string value!<br>"
            error += "In: txt_structures->{}".format(structure_name)
            raise ValueError(error)

        return True

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

        return True

        pass

    def _check_file_group(self, group):

        if "group_name" not in group or type(group["group_name"]) is not str or group["group_name"] == "":
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

        if "count_override" in group and (type(group["count"]) is not str or group["count_override"] == ""):
            error = "'count_override' attr must contain string value!<br>"
            error += "In: dat_files->groups->{}".format(group["group_name"])
            raise ValueError(error)

        if "structure" not in group or type(group["structure"]) is not str or group["structure"] == "":
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

        return True

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

        if "groups" not in file or type(file["output_file"]) is not str or file["groups"] == "":
            error = "'groups' attr is required and must contain a string value!<br>"
            error += "In: txt_files"
            raise ValueError(error)

        if "structure" not in file or type(file["output_file"]) is not str or file["structure"] == "":
            error = "'structure' attr is required and must contain a string value!<br>"
            error += "In: txt_files"
            raise ValueError(error)

        return True

        pass

    def _check_file_headers(self):

        for file in self.structure["dat_files"]:
            variables = []
            for group in file["groups"]:
                if "header" not in group:
                    continue
                for field in group["header"]:
                    if field["title"] in variables:
                        error = "Header field name '{}' already exist!<br>".format(field["title"])
                        error += "In: dat_files->groups->{}->header".format(group["group_name"])
                        raise ValueError(error)
                    variables.append(field["title"])
                # check 'count' attr
                count = group["count"]
                if type(count) is str:
                    # parse variables
                    founded_vars = re.findall("\{(.*?)\}", count)
                    for var in founded_vars:
                        if var not in variables:
                            error = "'count' attr refers to a non-existing variable: '{}'!<br>".format("{" + var + "}")
                            error += "In: dat_files->groups->{}->count".format(group["group_name"])
                            raise ValueError(error)
                        else:
                            count = count.replace("{" + var + "}", "1")
                    # check math expression
                    if re.search("^[0-9\-+ ]+$", count) is None:
                        error = "'count' attr contains wrong math expression: '{}'!<br>".format(group["count"])
                        error += "In: dat_files->groups->{}->count".format(group["group_name"])
                        raise ValueError(error)
                # check 'count_override' attr
                if "count_override" in group and group["count_override"] not in variables:
                    error = "'count_override' attr refers to a non-existing"
                    error += " header-field: '{}'!<br>".format(group["count_override"])
                    error += "In: dat_files->groups->{}->count_override".format(group["group_name"])
                    raise ValueError(error)

        return True

        pass

    def _check_file_names(self):

        # dat_files
        source_files = []
        header_files = []
        for file in self.structure["dat_files"]:
            source_file = file["side"] + "/" + file["source_file"]
            if source_file in source_files:
                error = "Duplicate source_file: '{}'!<br>".format(file["source_file"])
                error += "In: dat_files->source_file"
                raise ValueError(error)
            source_files.append(source_file)

            if file["header_file"] in header_files:
                error = "Duplicate header_file: '{}'!<br>".format(file["header_file"])
                error += "In: dat_files->header_file"
                raise ValueError(error)
            header_files.append(file["header_file"])

        # txt_files
        output_files = []
        for file in self.structure["txt_files"]:
            if file["output_file"] in output_files:
                error = "Duplicate output_file: '{}'!<br>".format(file["output_file"])
                error += "In: txt_files->output_file"
                raise ValueError(error)
            output_files.append(file["output_file"])

        return True

        pass

    def _check_structures_usage(self):

        # dat_files
        used = []
        for file in self.structure["dat_files"]:
            for group in file["groups"]:
                if group["structure"] not in self.structure["dat_structures"]:
                    error = "dat_file refers to a non existing dat_structure: '{}'!<br>".format(group["structure"])
                    error += "In: dat_files->groups->structure"
                    raise ValueError(error)
                if group["structure"] not in used:
                    used.append(group["structure"])
        if len(used) < len(self.structure["dat_structures"]):
            # some structure is never used
            for name in self.structure["dat_structures"]:
                if name not in used:
                    error = "dat_structure '{}' is never used!".format(name)
                    raise ValueError(error)

        # txt_files
        used = []
        for file in self.structure["txt_files"]:
            if file["structure"] not in self.structure["txt_structures"]:
                error = "txt_file refers to a non existing txt_structure: '{}'!<br>".format(file["structure"])
                error += "In: txt_files->structure"
                raise ValueError(error)
            if file["structure"] not in used:
                used.append(file["structure"])
        if len(used) < len(self.structure["txt_structures"]):
            # some structure is never used
            for name in self.structure["txt_structures"]:
                if name not in used:
                    error = "txt_structure '{}' is never used!".format(name)
                    raise ValueError(error)

        return True

        pass

    def _check_groups_usage(self):

        # check groups duplicate names, create groups map (group -> dat_file)
        groups = {}
        for index, dat_file in enumerate(self.structure["dat_files"]):
            for group in dat_file["groups"]:
                if group["group_name"] in groups:
                    error = "Duplicate group name: '{}'!<br>".format(group["group_name"])
                    error += "In: dat_files->groups"
                    raise ValueError(error)
                groups[group["group_name"]] = index
        # check groups usage
        used_groups = []
        for txt_file in self.structure["txt_files"]:
            for used in txt_file["groups"].split("|"):
                if used not in groups:
                    error = "'groups' attr refers to a non-existing group: '{}'!<br>".format(used)
                    error += "In: txt_files->groups"
                    raise ValueError(error)
                if used in used_groups:
                    error = "Group '{}' should be used only one time!<br>".format(used)
                    error += "In: txt_files->groups"
                    raise ValueError(error)
                used_groups.append(used)

        if len(used_groups) < len(groups):
            # some groups is never used
            for group in groups:
                if group not in used_groups:
                    error = "Group '{}' is never used!<br>".format(group)
                    error += "In: dat_files->groups"
                    raise ValueError(error)

        return True

        pass

    def _check_fields_linking(self):

        # create fields map
        dat_map = {}
        for name, data in self.structure["dat_structures"].items():
            dat_map[name] = self._get_structure_fields_map(data)

        txt_map = {}
        for name, data in self.structure["txt_structures"].items():
            txt_map[name] = self._get_structure_fields_map(data)

        groups_map = self._get_groups_map()

        # check txt linking
        for file in self.structure["txt_files"]:
            groups = file["groups"].split("|")
            for field in txt_map[file["structure"]]["fields"]:
                if field["from"] not in groups:
                    error = "Field refers to a non-existing group: '{}'!<br>".format(field["from"])
                    error += "In: txt_structures->{}".format(field["title"])
                    raise ValueError(error)

                used_structure = groups_map[field["from"]]["dat_structure"]
                if field["field"] not in dat_map[used_structure]["titles"]:
                    error = "'field' attr refers to a non-existing dat-field: '{}'!<br>".format(field["field"])
                    error += "In: txt_structures->{}->{}".format(file["structure"], field["title"])
                    raise ValueError(error)

        # check dat linking
        for file in self.structure["dat_files"]:
            for group in file["groups"]:
                past_fields = []
                for field in dat_map[group["structure"]]["fields"]:
                    used_structure = groups_map[group["group_name"]]["txt_structure"]
                    if "use" in field and field["use"] not in txt_map[used_structure]["titles"]:
                        error = "'use' attr refers to a non-existing txt-field: '{}'!<br>".format(field["use"])
                        error += "In: dat_structures->{}->{}".format(group["structure"], field["title"])
                        raise ValueError(error)

                    if field["type"] == "cstr" and "len" in field and type(field["len"]) is str:
                        used_field = field["len"].strip("{}")
                        if used_field not in past_fields:
                            error = "Unknown variable in 'len' attr: '{}'!<br>".format(field["len"])
                            error += "In: dat_structures->{}->{}".format(group["structure"], field["title"])
                            raise ValueError(error)
                    past_fields.append(field["title"])

        return True

        pass

    @staticmethod
    def _get_structure_fields_map(structure):

        data = {
            "titles": [],
            "types": {},
            "fields": [],
            "from": []
        }

        for field in structure:
            if "repeat" in field:
                for loop in range(field["repeat"]):
                    for repeated in field["fields"]:
                        row = repeated.copy()

                        if re.search("\{loop\}", row["title"]):
                            row["title"] = row["title"].replace("{loop}", str(loop + 1))
                        if "use" in repeated and re.search("\{loop\}", repeated["use"]):
                            row["use"] = row["use"].replace("{loop}", str(loop + 1))
                        if "field" in repeated and re.search("\{loop\}", repeated["field"]):
                            row["field"] = row["field"].replace("{loop}", str(loop + 1))

                        data["fields"].append(row)
                        data["titles"].append(row["title"])
                        if "type" in row:
                            data["types"][row["title"]] = row["type"]
                        if "from" in row:
                            data["from"].append(row["from"] + " -> " + row["field"])
            else:
                data["fields"].append(field)
                data["titles"].append(field["title"])
                if "type" in field:
                    data["types"][field["title"]] = field["type"]
                if "from" in field:
                    data["from"].append(field["from"] + " -> " + field["field"])

        return data

        pass

    def _get_groups_map(self):

        groups_map = {}
        for index, file in enumerate(self.structure["dat_files"]):
            for group in file["groups"]:
                groups_map[group["group_name"]] = {
                    "dat_file_index": index,
                    "dat_structure": group["structure"]
                }
        for index, file in enumerate(self.structure["txt_files"]):
            used = file["groups"].split("|")
            for group in used:
                groups_map[group]["txt_file_index"] = index
                groups_map[group]["txt_structure"] = file["structure"]

        return groups_map

        pass

    def _read_structure_file(self):

        try:
            file = open(self.file_path, "r")
            structure = file.read()
            file.close()
            structure = json.loads(structure)
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

    @staticmethod
    def _callback_dummy(*values):

        print("Structure Class: %s" % list(values))

        pass

    pass
