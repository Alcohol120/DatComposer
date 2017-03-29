from application.config import *
from .File import File
from application.composer.Rules import rules
import re
import math
import json
from struct import pack


class DATFile(File):

    def __init__(self, file_name, file_path, paths, structure=None):

        super().__init__(file_name, file_path, paths)

        if structure is None:
            structure = dict()

        self.structure = structure
        self.meta = {}

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
            except Exception as error:
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

    def build(self, txt_data, groups_map):

        result_data = []

        for group in self.structure["groups"]:

            status_text = "Writing file: {} [{}]".format(self.get_name(), group["group_name"])
            self.callbacks["current_progress_text"](status_text)

            group_map = groups_map[group["group_name"]]["map"]
            txt_file = txt_data[groups_map[group["group_name"]]["file"]]

            # progress
            total_rows = len(txt_file)
            percent = math.floor(total_rows / 100)
            if percent < 1:
                percent = 1
            count = 0

            # header
            header = self._build_header(group, total_rows)
            if not header["success"]:
                return header
            result_data.extend(header["header"])

            # group body
            while count < total_rows:
                cells = []
                for field in group["structure"]["fields"]:
                    if self.canceled:
                        self.canceled = False
                        return {
                            "success": False,
                            "error": "Operation canceled by user!"
                        }
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
                        try:
                            value = getattr(rules, field["rule"])(value)
                        except Exception as e:
                            return {
                                "success": False,
                                "error": str(e)
                            }

                    if field["type"] == "cstr":
                        if "len" not in field:
                            result = self._pack_bytes(value, "cstr", 64)
                        elif type(field["len"]) is int:
                            result = self._pack_bytes(value, "cstr", field["len"])
                        else:
                            result = self._pack_bytes(value, "cstr", len(value) + 1)
                    else:
                        result = self._pack_bytes(value, field["type"])

                    if type(result) is dict:
                        return {
                            "success": False,
                            "error": result["msg"]
                        }
                    cells.append(result)

                result_data.append(b"".join(cells))
                count += 1
                if count % percent == 0:
                    self.callbacks["current_progress"](count / percent)

            self.output = b"".join(result_data)
            self.callbacks["step_completed"]()

        return {"success": True}

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

    def encode(self):

        self.reset()

        if not self.is_exists():
            return False

        if not self.read():
            return False

        output = b""

        crypt_bytes = self.crypt_bytes.copy()
        file_size = self.get_size()
        content = list(self.source)
        end = list(bytearray(256))

        percent = math.floor(file_size / 100)
        if percent < 1:
            percent = 1

        # start encoding
        i = 0
        while i < file_size:
            if self.canceled:
                self.canceled = False
                return False
            crypt_byte = crypt_bytes[(i + 1) % 256]
            if i & 1:
                content[i] -= crypt_byte
            else:
                content[i] += crypt_byte
            i += 1
            if i % percent == 0:
                self.callbacks["current_progress"](i / percent)

        content = self._bytes_range(content)

        i = 0
        while i < 0x100:
            if self.canceled:
                self.canceled = False
                return False
            temp = crypt_bytes[i]
            crypt_bytes[i] = crypt_bytes[i + 1]
            crypt_bytes[i + 1] = temp
            i += 2

        content = self._bytes_range(content)

        i = 0
        a = 255
        while i < 0x100:
            if self.canceled:
                self.canceled = False
                return False
            if i & 1:
                crypt_bytes[a] -= self.crypt_key[(i + 1) & 7]
            else:
                crypt_bytes[a] += self.crypt_key[(i + 1) & 7]
            end[i] = crypt_bytes[a]

            if (i - 1) & 1:
                crypt_bytes[a - 1] -= self.crypt_key[(i + 2) & 7]
            else:
                crypt_bytes[a - 1] += self.crypt_key[(i + 2) & 7]
            end[i + 1] = crypt_bytes[a - 1]

            if (i & 1) == 1:
                crypt_bytes[a - 2] -= self.crypt_key[(i + 3) & 7]
            else:
                crypt_bytes[a - 2] += self.crypt_key[(i + 3) & 7]
            end[i + 2] = crypt_bytes[a - 2]

            if ((i - 1) & 1) == 1:
                crypt_bytes[a - 3] -= self.crypt_key[(i - 4) & 7]
            else:
                crypt_bytes[a - 3] += self.crypt_key[(i - 4) & 7]
            end[i + 3] = crypt_bytes[a - 3]
            a -= 4
            i += 4

        end = self._bytes_range(end)

        output += self.copyright.encode("windows-1251")
        output += pack("I", file_size)
        output += bytes(content)
        output += bytes(end)

        # writing
        return output

        pass

    def reset(self):

        self.canceled = False
        self.source = b""
        self.output = b""
        self.meta = {}

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
        if percent < 1:
            percent = 1

        # read group body
        count = 0
        rows = []
        while count < total_rows:
            cells = []
            for field in group["structure"]["fields"]:
                if self.canceled:
                    self.canceled = False
                    raise ValueError("Operation canceled by user!")
                size = self._get_field_len(field, group["structure"]["titles"], cells)
                if size == 0:
                    raise ValueError("{}: Can't get length of '{}' field!".format(group["group_name"], field["title"]))
                # read field
                field_data = self.source[offset:(offset + size)]
                field_data = self._unpack_bytes(field_data, field["type"])
                if type(field_data) is dict:
                    error = "{}: Can't read '{}' field!".format(group["group_name"], field["title"])
                    error += "<br>{}".format(field_data["msg"])
                    raise ValueError(error)
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
            if type(field_data) is dict:
                error = "{}: Can't read '{}' header field!".format(group["group_name"], field["title"])
                error += "<br>{}".format(field_data["msg"])
                raise ValueError(error)
            meta_vars[field["title"]] = field_data
            offset += size

        return {
            "meta": meta_vars,
            "offset": offset
        }

        pass

    def _build_header(self, group, rows_count):

        header = []

        if "header" in group:
            for field in group["header"]:
                if field["title"] not in self.meta:
                    return {
                        "success": False,
                        "error": "Can't find header variable: {}".format(field["title"])
                    }
                if "count_override" in group and field["title"] == group["count_override"]:
                    result = self._pack_bytes(rows_count, field["type"])
                elif field["type"] == "cstr":
                    if "len" in field or type(field["len"]) is int:
                        result = self._pack_bytes(self.meta[field["title"]], "cstr", field["len"])
                    else:
                        result = self._pack_bytes(self.meta[field["title"]], "cstr", 64)
                else:
                    result = self._pack_bytes(self.meta[field["title"]], field["type"])
                if type(result) is dict:
                    raise ValueError(result["msg"])
                header.append(result)

        return {
            "success": True,
            "header": header
        }

        pass

    @staticmethod
    def _get_total_rows(group, meta_vars):

        total_rows = -1
        if type(group["count"]) is str:
            if re.search("^[0-9]+$", group["count"].strip()) is not None:
                return int(group["count"])
            founded_vars = re.findall("\{(.*?)\}", group["count"])
            for var in founded_vars:
                total_rows = group["count"].replace("{" + var + "}", str(meta_vars[var]))
            if re.search("^[0-9\-+ ]+$", total_rows) is None:
                return -1
            total_rows = int(eval(total_rows))
        else:
            total_rows = group["count"]

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

    pass
