from .File import File
import math
from struct import unpack


class EDFFile(File):

    def decode(self):

        self.reset()

        if not self.is_exists():
            return False

        if not self.read():
            return False

        block_size = unpack("I", self.source[29:29 + 4])[0]

        content = list(self.source[29 + 4:29 + 4 + block_size])
        end = list(self.source[29 + 4 + block_size:29 + 4 + block_size + 256])

        decrypt_data = list(bytearray(256))

        i = 0
        a = 255
        while i < 0x100:
            if self.canceled:
                self.canceled = False
                return False
            if i & 1:
                end[i] += self.crypt_key[(i + 1) & 7]
            else:
                end[i] -= self.crypt_key[(i + 1) & 7]
            decrypt_data[a] = end[i]

            if (i - 1) & 1:
                end[i + 1] += self.crypt_key[(i + 2) & 7]
            else:
                end[i + 1] -= self.crypt_key[(i + 2) & 7]
            decrypt_data[a - 1] = end[i + 1]

            if (i & 1) == 1:
                end[i + 2] += self.crypt_key[(i + 3) & 7]
            else:
                end[i + 2] -= self.crypt_key[(i + 3) & 7]
            decrypt_data[a - 2] = end[i + 2]

            if ((i - 1) & 1) == 1:
                end[i + 3] += self.crypt_key[(i + 4) & 7]
            else:
                end[i + 3] -= self.crypt_key[(i + 4) & 7]
            decrypt_data[a - 3] = end[i + 3]
            a -= 4
            i += 4

        decrypt_data = self._bytes_range(decrypt_data)

        i = 0
        while i < 0x100:
            if self.canceled:
                self.canceled = False
                return False
            temp = decrypt_data[i]
            decrypt_data[i] = decrypt_data[i + 1]
            decrypt_data[i + 1] = temp
            i += 2

        decrypt_data = self._bytes_range(decrypt_data)

        percent = math.floor(block_size / 100)

        i = 0
        while i < block_size:
            if self.canceled:
                self.canceled = False
                return False
            decrypt_byte = decrypt_data[(i + 1) % 256]
            if i & 1:
                content[i] += decrypt_byte
            else:
                content[i] -= decrypt_byte
            i += 1
            if i % percent == 0:
                self.callbacks["current_progress"](i / percent)

        content = self._bytes_range(content)

        return bytes(content)

        pass

    def reset(self):

        self.canceled = False
        self.source = b""
        self.output = b""

        pass

    pass
