from .File import File


class DATFile(File):

    def __init__(self, file_name, file_path, side):

        super().__init__(file_name, file_path)
        self.side = side

        pass

    def get_side(self):

        return self.side

        pass

    pass
