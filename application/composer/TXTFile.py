from .File import File


class TXTFile(File):

    def __init__(self, file_name, file_path, data):

        super().__init__(file_name, file_path)

        self.data = data

        self.callback = object

        pass

    pass
