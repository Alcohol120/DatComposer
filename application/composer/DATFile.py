from .File import File
import re
import math
from struct import pack, unpack


class DATFile(File):

    def __init__(self, file_name, file_path, structure):

        super().__init__(file_name, file_path)

        self.structure = structure

        self.callbacks = {
            "update_progress": self._callback_dummy,
            "update_progress_text": self._callback_dummy,
            "step_completed": self._callback_dummy
        }

        pass

    def get_side(self):

        if "side" in self.structure:
            return self.structure["side"]
        else:
            return False

        pass

    def set_callbacks(self, callbacks):

        if "update_progress" in callbacks:
            self.callbacks["update_progress"] = callbacks["update_progress"]

        if "update_progress_text" in callbacks:
            self.callbacks["update_progress_text"] = callbacks["update_progress_text"]

        if "step_completed" in callbacks:
            self.callbacks["step_completed"] = callbacks["step_completed"]

        pass

    def parse(self):

        file_name = self.get_name()

        if self.source == "":
            return {
                "success": False,
                "error": "Can't read file data!"
            }

        offset = 0
        meta_vars = {}
        groups_data = {}

        # parse file by groups
        for group in self.structure["groups"]:
            status_text = "Reading file: {} [{}]".format(file_name, group["group_name"])
            self.callbacks["update_progress_text"](status_text)
            try:
                result = self._parse_group(group, meta_vars, offset)
            except ValueError as error:
                return {
                    "success": False,
                    "error": str(error)
                }
            offset = result["offset"]
            meta_vars = result["meta_vars"]
            groups_data[group["group_name"]] = result["rows"]
            self.callbacks["step_completed"]()

        return {
            "success": True,
            "data": groups_data
        }

        pass

    def _parse_group(self, group, meta, offset):

        meta_vars = meta

        # read header
        if "header" in group:
            for field in group["header"]:
                size = self._get_field_len(field)
                if size == 0:
                    error = "{}: Can't get length of '{}' field!".format(group["group_name"], field["title"])
                    raise ValueError(error)
                # read field
                field_data = self.source[offset:(offset + size)]
                field_data = self._unpack_bytes(field_data, field["type"])
                if field_data is Exception:
                    error = "{}: Can't read '{}' field!".format(group["group_name"], field["title"])
                    raise ValueError(error)
                meta_vars[field["title"]] = field_data
                offset += size

        # get total rows
        total_rows = self._get_total_rows(group, meta_vars)
        if total_rows < 1:
            error = "{}: Wrong 'count' parameter!".format(group["group_name"])
            raise ValueError(error)

        # progress
        percent = math.floor(total_rows / 100)
        percent_step = 1
        if total_rows < 500:
            percent_step = 25
        elif total_rows < 1000:
            percent_step = 20
        elif total_rows < 2000:
            percent_step = 10
        elif total_rows < 3000:
            percent_step = 5

        # read group body
        count = 0
        rows = []
        while count < total_rows:
            cells = []
            for field in group["structure"]["fields"]:
                size = self._get_field_len(field, group["structure"]["titles"], cells)
                if size == 0:
                    error = "{}: Can't get length of '{}' field!".format(group["group_name"], field["title"])
                    raise ValueError(error)
                # read field
                field_data = self.source[offset:(offset + size)]
                field_data = self._unpack_bytes(field_data, field["type"])
                if field_data is Exception:
                    error = "{}: Can't read '{}' field!".format(group["group_name"], field["title"])
                    raise ValueError(error)
                cells.append(field_data)
                offset += size
            rows.append(cells)
            count += 1
            if count % (percent * percent_step) == 0:
                self.callbacks["update_progress"](count / percent)

        return {
            "rows": rows,
            "offset": offset,
            "meta_vars": meta_vars
        }

        pass

    @staticmethod
    def _get_total_rows(group, meta_vars):

        total_rows = 0
        if type(group["count"]) is str:
            founded_vars = re.findall("\{(.*?)\}", group["count"])
            for var in founded_vars:
                total_rows = group["count"].replace("{" + var + "}", str(meta_vars[var]))
            if re.search("^[0-9\-+ ]+$", total_rows) is None:
                return 0
            total_rows = int(eval(total_rows))
        else:
            total_rows = int(group["count"])
        if total_rows < 1:
            return 0

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
                src = src.strip(" \x00")
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

    pass
