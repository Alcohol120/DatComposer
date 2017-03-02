import re


class Rules:

    @staticmethod
    def race_bm(value):
        value = str(value)
        value = value.strip()
        if re.search("^[0-1]{0,5}$", value) is None:
            return 0
        value += "00000"
        return value[0]
        pass

    @staticmethod
    def race_bf(value):
        value = str(value)
        value = value.strip()
        if re.search("^[0-1]{0,5}$", value) is None:
            return 0
        value += "00000"
        return value[1]
        pass

    @staticmethod
    def race_cm(value):
        value = str(value)
        value = value.strip()
        if re.search("^[0-1]{0,5}$", value) is None:
            return 0
        value += "00000"
        return value[2]
        pass

    @staticmethod
    def race_cf(value):
        value = str(value)
        value = value.strip()
        if re.search("^[0-1]{0,5}$", value) is None:
            return 0
        value += "00000"
        return value[3]
        pass

    @staticmethod
    def race_a(value):
        value = str(value)
        value = value.strip()
        if re.search("^[0-1]{0,5}$", value) is None:
            return 0
        value += "00000"
        return value[4]
        pass

    @staticmethod
    def item_code(value):
        code = value[0:2]
        if code == "if":
            return 0
        elif code == "iu":
            return 1
        elif code == "il":
            return 2
        elif code == "ig":
            return 3
        elif code == "is":
            return 4
        elif code == "ih":
            return 5
        elif code == "iw":
            return 6
        elif code == "id":
            return 7
        elif code == "ik":
            return 8
        elif code == "ii":
            return 9
        elif code == "ia":
            return 10
        elif code == "ib":
            return 11
        elif code == "im":
            return 12
        elif code == "ip":
            return 13
        elif code == "ie":
            return 14
        elif code == "it":
            return 15
        elif code == "io":
            return 16
        elif code == "ir":
            return 17
        elif code == "ic":
            return 18
        elif code == "in":
            return 19
        elif code == "iy":
            return 20
        elif code == "iz":
            return 21
        elif code == "iq":
            return 22
        elif code == "ix":
            return 23
        elif code == "ij":
            return 24
        elif code == "gt":
            return 25
        elif code == "tr":
            return 26
        elif code == "sk":
            return 27
        elif code == "ti":
            return 28
        elif code == "ey":
            return 29
        elif code == "re":
            return 30
        elif code == "bx":
            return 31
        elif code == "fi":
            return 32
        elif code == "un":
            return 33
        elif code == "rd":
            return 34
        elif code == "lk":
            return 35
        elif code == "cu":
            return 36
        else:
            return 255
        pass

    def item_id(self, value):

        if self.item_code(value) == 255:
            return "$FFFFFFFF"

        abc = "abcdefghijklmnopqrstuvwxyz"

        hex_word = ""
        for loop, char in enumerate(value[2:5]):
            for c_loop, c_char in enumerate(abc):
                if char == c_char:
                    if loop == 0:
                        r = hex(c_loop + 192)
                        r = r[2:4]
                        if len(r) < 2:
                            r = "0" + r
                        hex_word += r
                    else:
                        r = hex(c_loop)
                        r = r[2:4]
                        if len(r) < 2:
                            r = "0" + r
                        hex_word += r

        hex_word = hex_word.upper()
        if len(hex_word) < 5:
            result = "$" + hex_word + str(value[5:7]) + "00"
        else:
            result = "$" + hex_word + str(value[5:7])

        return result
        pass

    @staticmethod
    def length(value):

        length = len(value)
        if length > 0:
            length += 1
        else:
            length = 2
        return length

        pass

    pass

rules = Rules()
