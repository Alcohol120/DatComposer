import re


class Rules:

    # @TODO refactoring

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
        try:
            item_group_code = {
                "if": 0,
                "iu": 1,
                "il": 2,
                "ig": 3,
                "is": 4,
                "ih": 5,
                "iw": 6,
                "id": 7,
                "ik": 8,
                "ii": 9,
                "ia": 10,
                "ib": 11,
                "im": 12,
                "ip": 13,
                "ie": 14,
                "it": 15,
                "io": 16,
                "ir": 17,
                "ic": 18,
                "in": 19,
                "iy": 20,
                "iz": 21,
                "iq": 22,
                "ix": 23,
                "ij": 24,
                "gt": 25,
                "tr": 26,
                "sk": 27,
                "ti": 28,
                "ey": 29,
                "re": 30,
                "bx": 31,
                "fi": 32,
                "un": 33,
                "rd": 34,
                "lk": 35,
                "cu": 36
            }[value[0:2]]
        except KeyError:
            item_group_code = 255
        return item_group_code
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
