from .File import File
from struct import pack, unpack


class DATFile(File):

    def __init__(self, file_name, file_path, structure):

        super().__init__(file_name, file_path)

        self.structure = structure

        self.callback = object

        pass

    def get_side(self):

        if "side" in self.structure:
            return self.structure["side"]
        else:
            return False

        pass

    def set_callback(self, callback):

        self.callback = callback

        pass

    def get_total_rows(self):

        total = 0

        if self.source == "":
            return total

        header = {}
        offset = 0
        for group in self.structure["groups"]:
            # read header fields
            if "header" in group:
                for field in group["header"]:
                    # get byte size of field
                    size = 0
                    if "len" not in field:
                        size = self._get_byte_length(field["type"])
                    else:
                        size = int(field["len"])
                    # read field
                    data = self.source[offset:(offset + size)]
                    data = self._unpack_bytes(data, field["type"])
                    header[field["title"]] = data
                    offset += size
            # get count
            if type(group["count"]) is int:
                total += int(group["count"])

        return total

        pass

    def parse(self):

        print("Start parsing: {}".format(self.file_name))

        i = 0
        while True:
            if i == 20000000:
                break
            i += 1

        print("Parsing finished: {}".format(self.file_name))

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
        except Exception:
            return None

        pass

    @staticmethod
    def _get_byte_length(d_type):

        if d_type == "i8":
            return 1,
        elif d_type == "i16":
            return 2
        elif d_type == "i32":
            return 4
        elif d_type == "u8":
            return 1,
        elif d_type == "u16":
            return 2
        elif d_type == "u32":
            return 4
        elif d_type == "x8":
            return 1,
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
            return 1

        pass

    pass
