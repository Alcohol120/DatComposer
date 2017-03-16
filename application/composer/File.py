import os
from struct import pack, unpack


class File:

    def __init__(self, file_name, file_path, paths):

        self.file_name = file_name
        self.file_path = file_path
        self.paths = paths

        self.read_mode = "rb"
        self.write_mode = "wb"

        self.canceled = False

        self.source = b""
        self.output = b""

        self.callbacks = {
            "current_progress": self._callback_dummy,
            "current_progress_text": self._callback_dummy,
            "step_completed": self._callback_dummy
        }

        self.crypt_bytes = [0x10, 0x57, 0x4F, 0x74, 0x67, 0x6D, 0x43, 0x67, 0x4E, 0x6C, 0x45,
                            0x74, 0x55, 0x66, 0x54, 0x71, 0x52, 0x39, 0x41, 0x4C, 0x4C, 0x5A,
                            0x42, 0x72, 0x6E, 0x69, 0x6F, 0x4F, 0x69, 0x7A, 0x66, 0x63, 0x76,
                            0x37, 0x38, 0x42, 0x47, 0x48, 0x57, 0x6E, 0x2B, 0x50, 0x4B, 0x48,
                            0x49, 0x79, 0x4B, 0x63, 0x39, 0x67, 0x74, 0x39, 0x73, 0x47, 0x36,
                            0x58, 0x73, 0x4C, 0x65, 0x35, 0x55, 0x51, 0x59, 0x52, 0x38, 0x50,
                            0x58, 0x6D, 0x6F, 0x47, 0x4C, 0x66, 0x6F, 0x80, 0xA6, 0x90, 0xCD,
                            0x8E, 0x20, 0x71, 0x54, 0x4F, 0x18, 0x98, 0x30, 0x57, 0x40, 0x53,
                            0x48, 0x6E, 0x51, 0x6A, 0x4C, 0x4B, 0x4D, 0x74, 0x67, 0x46, 0x4B,
                            0x63, 0x51, 0x4A, 0x4B, 0x6D, 0x50, 0x51, 0x32, 0x51, 0x55, 0x55,
                            0x46, 0x57, 0x34, 0x6A, 0x79, 0x68, 0x6B, 0x33, 0x50, 0x70, 0x55,
                            0x58, 0x31, 0x72, 0x4B, 0x67, 0x6B, 0x45, 0x74, 0x4F, 0x61, 0x6B,
                            0x42, 0x49, 0x34, 0x36, 0x2E, 0x5C, 0x6D, 0x61, 0x70, 0x5C, 0x4E,
                            0x65, 0x75, 0x74, 0x72, 0x61, 0x6C, 0x42, 0x5C, 0x4E, 0x65, 0x75,
                            0x74, 0x72, 0x61, 0x6C, 0x42, 0x2E, 0x42, 0x53, 0x50, 0x50, 0x44,
                            0x41, 0x50, 0x6A, 0x32, 0x47, 0x75, 0x54, 0x70, 0x52, 0x69, 0x53,
                            0x75, 0x41, 0x66, 0x56, 0x49, 0x5A, 0x67, 0x63, 0x4E, 0x65, 0x35,
                            0x6C, 0x5A, 0x67, 0x46, 0x6D, 0x54, 0x4E, 0x47, 0x72, 0x30, 0x32,
                            0x79, 0x53, 0x34, 0x61, 0x75, 0x61, 0x51, 0x72, 0x77, 0x4B, 0x34,
                            0x67, 0x48, 0x6B, 0x49, 0x59, 0x6F, 0x54, 0x61, 0x79, 0x34, 0x68,
                            0x4C, 0x63, 0x33, 0x4D, 0x66, 0x4E, 0x6D, 0x57, 0x7A, 0x44, 0x65,
                            0x4B, 0x4A, 0x74, 0x37, 0x51, 0x35, 0x52, 0x39, 0x79, 0x63, 0x75,
                            0x74, 0x66, 0x6D, 0x55, 0x75, 0x53, 0x2B, 0x62, 0x59, 0x2B, 0x39,
                            0x39, 0x7A, 0x41, 0xBC, 0x24]
        self.crypt_key = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]
        self.copyright = "RF Online by OdinTeam s(^O^)z"

        pass

    def get_name(self):

        return self.file_name

        pass

    def get_path(self):

        catalogs = self.get_full_path()

        catalogs = catalogs.split("/")
        if len(catalogs) > 1:
            catalogs.reverse()
            del catalogs[0]
            catalogs.reverse()
        return "/".join(catalogs)

        pass

    def get_full_path(self):

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

    def get_size(self):

        return os.path.getsize(self.file_path)

        pass

    def read(self):

        try:
            file = open(self.file_path, self.read_mode)
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

    def write(self, output):

        return self.save(output)

        pass

    def save(self, output=None):

        if output is None:
            data = self.output
        else:
            data = output

        file_path = self.get_path()

        if not os.path.exists(file_path):
            try:
                os.makedirs(file_path)
            except IsADirectoryError:
                return False

        try:
            file = open(self.file_path, self.write_mode)
            file.write(data)
            file.close()
        except PermissionError:
            return False
        except FileNotFoundError:
            return False

        return True

        pass

    def cancel_task(self):

        self.canceled = True

        pass

    # Private Methods

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
    def _bytes_range(bytes_list):

        for i, b in enumerate(bytes_list):
            if b < 0:
                bytes_list[i] = b % 256
            elif b > 255:
                bytes_list[i] = b % 256
        return bytes_list

        pass

    @staticmethod
    def _callback_dummy(*values):

        print("File Class: %s" % list(values))

        pass

    pass
