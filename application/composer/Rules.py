import re
import math


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

    def item_type(self, value):

        code = value[0:2]
        result = self._get_item_type(code)
        if result == -1:
            return 255
        else:
            return result

        pass

    def item_type_negative(self, value):

        code = value[0:2]
        return self._get_item_type(code)

        pass

    def item_id(self, value):

        if value == -1 or value == "-1":
            return "$FFFFFFFF"

        if self.item_type(value) == 255:
            return "$FFFFFFFF"

        result = self._convert_id(value)

        item_code = value[0:2]
        if item_code == "gt":
            result = result.replace("$C", "$A")
        elif item_code == "tr":
            if len(result) < 9:
                result += "0" * (9 - len(result))
                result = result.replace("$0", "$7")
                result = result.replace("$1", "$8")
                result = result.replace("$2", "$9")
                result = result.replace("$3", "$A")
                result = result.replace("$4", "$B")
                result = result.replace("$5", "$C")
                result = result.replace("$6", "$D")
                result = result.replace("$7", "$E")
            else:
                result = result.replace("$C", "$7")
        elif item_code == "sk":
            result = result.replace("$C", "$6")
        elif item_code == "ti":
            result = result.replace("$C", "$7")
        elif item_code == "ev":
            result = result.replace("$C", "$8")
        elif item_code == "re":
            result = result.replace("$C", "$5")
        elif item_code == "bx":
            result = result.replace("$C", "$5")
            result = result.replace("$D", "$6")
        elif item_code == "fi":
            result = result.replace("$C", "$9")
        elif item_code == "un":
            result = result.replace("$C", "$8")
        elif item_code == "rd":
            result = result.replace("$C", "$5")
        elif item_code == "lk":
            result = result.replace("$C", "$F")
        elif item_code == "cu":
            result = result.replace("$C", "$6")

        return result

        pass

    def unit_id(self, value):

        if value == -1:
            return "$FFFFFFFF"

        if self.item_type(value) == 255:
            return "$FFFFFFFF"

        result = self._convert_id(value)

        item_code = value[0:3]
        if item_code == "unh" or item_code == "unl" or item_code == "una" or item_code == "unb":
            result.replace("$C", "$8")
        elif item_code == "unu" or item_code == "uns":
            result.replace("$C", "$9")

        return result

        pass

    @staticmethod
    def npc_id(value):

        if value == "-1" or value == "0":
            return "$FFFFFFFF"

        npc_code = value
        if re.search("^0.*?", value) is not None:
            npc_code = value[1:len(value)]
        npc_code = "$" + npc_code

        return npc_code

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

    @staticmethod
    def not_none(value):

        if value == "-1" or value == "0":
            return 0
        else:
            return 1

        pass

    pass

    @staticmethod
    def hash_tag(value):

        return "#" + str(value)

        pass

    pass

    @staticmethod
    def fix_byte(value):

        a = int(value)

        if a < 0:
            a = int(math.fabs(a))

        if a > 127:
            c = a % 128
            return -128 + c
        else:
            return value

        pass

    @staticmethod
    def _get_item_type(code):

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
        elif code == "ev":
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
            return -1

        pass

    @staticmethod
    def _convert_id(value):

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

rules = Rules()
