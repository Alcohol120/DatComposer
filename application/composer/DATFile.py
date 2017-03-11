from application.config import *
from .File import File
from application.composer.Rules import rules
import re
import math
import json
from struct import pack, unpack


class DATFile(File):

    def __init__(self, file_name, file_path, paths, structure):

        super().__init__(file_name, file_path, paths)

        self.structure = structure
        self.meta = {}
        self.groups_data = {}

        pass

    def get_side(self):

        if "side" in self.structure:
            return self.structure["side"]
        else:
            return False

        pass

    def parse(self):

        self.meta = {}

        if self.source == "":
            return {
                "success": False,
                "error": "Can't read file data!"
            }

        offset = 0
        groups_data = {}

        # parse file by groups
        for group in self.structure["groups"]:

            status_text = "Reading file: {} [{}]".format(self.get_name(), group["group_name"])
            self.callbacks["current_progress_text"](status_text)

            try:
                result = self._parse_group(group, offset)
            except ValueError as error:
                return {
                    "success": False,
                    "error": str(error)
                }

            offset = result["offset"]
            self.meta = result["meta_vars"]
            groups_data[group["group_name"]] = result["rows"]

            self.callbacks["step_completed"]()

        return {
            "success": True,
            "data": groups_data
        }

        pass

    def save_meta(self):

        path = ROOT_PATH + "/" + self.paths["txt"] + "/" + self.structure["catalog_name"] + "/meta"

        if not os.path.isdir(path):
            os.makedirs(path)

        data = json.dumps(self.meta, sort_keys=True, indent=4)

        try:
            file = open(path + "/" + self.structure["header_file"], "w")
            file.write(data)
            file.close()
        except PermissionError:
            return False
        except FileNotFoundError:
            return False

        return True

        pass

    def load_meta(self):

        path = ROOT_PATH + "/" + self.paths["txt"] + "/" + self.structure["catalog_name"] + "/meta/" \
               + self.structure["header_file"]

        try:
            file = open(path, "r")
            data = file.read()
            self.meta = json.loads(data)
            file.close()
        except PermissionError:
            return False
        except FileNotFoundError:
            return False
        except ValueError:
            return False

        return True

        pass

    def build(self, txt_data, groups_map):

        self.groups_data = {}

        for group in self.structure["groups"]:

            status_text = "Composing file: {} [{}]".format(self.get_name(), group["group_name"])
            self.callbacks["current_progress_text"](status_text)

            group_map = groups_map[group["group_name"]]["map"]
            txt_file = txt_data[groups_map[group["group_name"]]["file"]]

            total_rows = len(txt_file)
            percent = math.floor(total_rows / 100)
            count = 0
            self.groups_data[group["group_name"]] = []
            while count < total_rows:
                cells = []
                for field in group["structure"]["fields"]:
                    if "value" in field:
                        if re.search("\{count\}", field["value"]) is not None:
                            value = field["value"].replace("{count}", str(count))
                        else:
                            value = field["value"]
                    else:
                        if "use" in field:
                            cell = group_map["titles"].index(field["use"])
                        elif group["group_name"] + " -> " + field["title"] in group_map["from"]:
                            cell = group_map["from"].index(group["group_name"] + " -> " + field["title"])
                        else:
                            cell = -1
                        if cell < 0 or cell >= len(txt_file[count]):
                            value = self._get_default_value(field)
                        else:
                            value = str(txt_file[count][cell])

                    if "rule" in field:
                        value = getattr(rules, field["rule"])(value)

                    if field["type"] == "cstr":
                        if "len" not in field:
                            result = self._pack_bytes(value, "cstr", 64)
                        elif type(field["len"]) is int:
                            result = self._pack_bytes(value, "cstr", field["len"])
                        else:
                            result = self._pack_bytes(value, "cstr", len(value) + 1)
                    else:
                        result = self._pack_bytes(value, field["type"])

                    if type(result) is ValueError:
                        return {
                            "success": False,
                            "error": str(result)
                        }
                    cells.append(result)

                self.groups_data[group["group_name"]].append(cells)
                count += 1
                if count % percent == 0:
                    self.callbacks["current_progress"](count / percent)

            self.callbacks["step_completed"]()

        return {"success": True}

        pass

    def save(self):

        output = b""

        if not self.get_name():
            return {
                "success": False,
                "error": "Can't read header file: {}".format(self.structure["header_file"])
            }

        for group in self.structure["groups"]:
            status_text = "Writing file: {} [{}]".format(self.get_name(), group["group_name"])
            self.callbacks["current_progress_text"](status_text)

            if "header" in group:
                for field in group["header"]:
                    if field["title"] not in self.meta:
                        return {
                            "success": False,
                            "error": "Can't find header variable: {}".format(field["title"])
                        }
                    if "count_override" in group and field["title"] == group["count_override"]:
                        result = self._pack_bytes(len(self.groups_data[group["group_name"]]), field["type"])
                    elif field["type"] == "cstr":
                        if "len" in field or type(field["len"]) is int:
                            result = self._pack_bytes(self.meta[field["title"]], "cstr", field["len"])
                        else:
                            result = self._pack_bytes(self.meta[field["title"]], "cstr", 64)
                    else:
                        result = self._pack_bytes(self.meta[field["title"]], field["type"])
                    output += result

            total_rows = len(self.groups_data[group["group_name"]])
            percent = math.floor(total_rows / 100)
            count = 0
            data = []
            for cells in self.groups_data[group["group_name"]]:
                row = b"".join(cells)
                data.append(row)
                count += 1
                if count % percent == 0:
                    self.callbacks["current_progress"](count / percent)
            data = b"".join(data)
            output += data

            self.callbacks["step_completed"]()

        if not self._write(output, self.structure["side"]):
            return {
                "success": False,
                "error": "Can't write file: {}".format(self.file_name)
            }

        return {"success": True}

        pass

    def reset(self):

        self.source = ""
        self.meta = {}
        self.groups_data = {}

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

    def _parse_group(self, group, offset):

        meta_vars = self.meta.copy()

        # read header
        if "header" in group:
            data = self._parse_header(group, offset)
            offset = data["offset"]
            meta_vars.update(data["meta"])

        # get total rows
        total_rows = self._get_total_rows(group, meta_vars)
        if total_rows < 0:
            raise ValueError("{}: Wrong 'count' parameter!".format(group["group_name"]))

        # progress
        percent = math.floor(total_rows / 100)

        # read group body
        count = 0
        rows = []
        while count < total_rows:
            cells = []
            for field in group["structure"]["fields"]:
                size = self._get_field_len(field, group["structure"]["titles"], cells)
                if size == 0:
                    raise ValueError("{}: Can't get length of '{}' field!".format(group["group_name"], field["title"]))
                # read field
                field_data = self.source[offset:(offset + size)]
                field_data = self._unpack_bytes(field_data, field["type"])
                if type(field_data) is ValueError:
                    raise ValueError("{}: Can't read '{}' field!".format(group["group_name"], field["title"]))
                cells.append(field_data)
                offset += size
            rows.append(cells)
            count += 1
            if count % percent == 0:
                self.callbacks["current_progress"](count / percent)

        return {
            "rows": rows,
            "offset": offset,
            "meta_vars": meta_vars
        }

        pass

    def _parse_header(self, group, offset):

        meta_vars = {}

        for field in group["header"]:
            size = self._get_field_len(field)
            if size == 0:
                error = "{}: Can't get length of '{}' header field!".format(group["group_name"], field["title"])
                raise ValueError(error)
            # read field
            field_data = self.source[offset:(offset + size)]
            field_data = self._unpack_bytes(field_data, field["type"])
            if type(field_data) is ValueError:
                error = "{}: Can't read '{}' header field!".format(group["group_name"], field["title"])
                raise ValueError(error)
            meta_vars[field["title"]] = field_data
            offset += size

        return {
            "meta": meta_vars,
            "offset": offset
        }

        pass

    @staticmethod
    def _get_total_rows(group, meta_vars):

        total_rows = -1
        if type(group["count"]) is str:
            founded_vars = re.findall("\{(.*?)\}", group["count"])
            for var in founded_vars:
                total_rows = group["count"].replace("{" + var + "}", str(meta_vars[var]))
            if re.search("^[0-9\-+ ]+$", total_rows) is None:
                return -1
            total_rows = int(eval(total_rows))
        else:
            total_rows = int(group["count"])

        return total_rows

        pass

    def _get_field_len(self, field, fields_map=list(), cells=list()):

        if "len" not in field:
            return self._get_byte_length(field["type"])
        elif type(field["len"]) is int:
            return field["len"]
        elif type(field["len"]) is str:
            found = re.search("\{(.*?)\}", field["len"])
            if found is None:
                return 0
            var_name = str(found.group(1))
            if len(fields_map) < 1 or len(cells) < 1:
                return 0
            if var_name not in fields_map:
                return 0
            index = fields_map.index(var_name)
            if len(cells) > index:
                length = cells[index]
                if type(length) is int:
                    return length
                elif type(length) is str and re.search("^[0-9]+$", length) is not None:
                    return int(length)
                else:
                    return 0
            else:
                return 0

        pass

    @staticmethod
    def _unpack_bytes(src, d_type):

        try:
            if d_type == "u8":
                return unpack("B", src)[0]
            elif d_type == "u16":
                return unpack("H", src)[0]
            elif d_type == "u32":
                return unpack("I", src)[0]
            elif d_type == "i8":
                return unpack("b", src)[0]
            elif d_type == "i16":
                return unpack("h", src)[0]
            elif d_type == "i32":
                return unpack("i", src)[0]
            elif d_type == "x8":
                return hex(unpack("B", src)[0])
            elif d_type == "x16":
                return hex(unpack("H", src)[0])
            elif d_type == "x32":
                res = hex(unpack("I", src)[0])
                res = res.replace("0x", "$")
                res = res.upper()
                return res
            elif d_type == "float":
                return unpack("f", src)[0]
            elif d_type == "double":
                return unpack("d", src)[0]
            elif d_type == "cstr":
                src = src.decode("windows-1251")
                src = src.strip("\x00")
                return src
        except Exception as e:
            return e

        pass

    @staticmethod
    def _pack_bytes(src, d_type, length=0):

        try:
            if d_type == "u8":
                return pack("B", int(src))
            elif d_type == "u16":
                return pack("H", int(src))
            elif d_type == "u32":
                return pack("I", int(src))
            elif d_type == "i8":
                return pack("b", int(src))
            elif d_type == "i16":
                return pack("h", int(src))
            elif d_type == "i32":
                return pack("i", int(src))
            elif d_type == "x8":
                return pack("B", int(src, 16))
            elif d_type == "x16":
                return pack("H", int(src, 16))
            elif d_type == "x32":
                src = src.replace("$", "0x")
                src = int(src, 16)
                return pack("I", src)
            elif d_type == "float":
                return pack("f", float(src))
            elif d_type == "double":
                return pack("d", float(src))
            elif d_type == "cstr":
                if len(src) < length:
                    src += "\x00" * (length - len(src))
                src = src.encode("windows-1251")
                return src
        except Exception as e:
            return e

        pass

    @staticmethod
    def _get_byte_length(d_type):

        if d_type == "i8":
            return 1
        elif d_type == "i16":
            return 2
        elif d_type == "i32":
            return 4
        elif d_type == "u8":
            return 1
        elif d_type == "u16":
            return 2
        elif d_type == "u32":
            return 4
        elif d_type == "x8":
            return 1
        elif d_type == "x16":
            return 2
        elif d_type == "x32":
            return 4
        elif d_type == "float":
            return 4
        elif d_type == "double":
            return 8
        elif d_type == "cstr":
            return 64
        else:
            return 0

        pass

    @staticmethod
    def _get_default_value(field):

        if field["type"] == "i8":
            return 0
        elif field["type"] == "i16":
            return 0
        elif field["type"] == "i32":
            return 0
        elif field["type"] == "u8":
            return 0
        elif field["type"] == "u16":
            return 0
        elif field["type"] == "u32":
            return 0
        elif field["type"] == "x8":
            return "$FF"
        elif field["type"] == "x16":
            return "$FFFF"
        elif field["type"] == "x32":
            return "$FFFFFFFF"
        elif field["type"] == "float":
            return 0
        elif field["type"] == "double":
            return 0
        elif field["type"] == "cstr":
            return ""
        else:
            return 0

        pass

    def _write(self, data, side="server"):

        path = ROOT_PATH + "/"
        if side == "server":
            path += self.paths["srv_dat"] + "/"
        else:
            path += self.paths["cli_dat"] + "/"

        if not os.path.isdir(path):
            os.makedirs(path)

        try:
            file = open(path + "/" + self.file_name, "wb")
            file.write(data)
            file.close()
        except PermissionError:
            return False
        except FileNotFoundError:
            return False

        return True

        pass

    pass
