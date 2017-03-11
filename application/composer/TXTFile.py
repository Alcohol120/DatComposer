from application.config import *
from .File import File
import math


class TXTFile(File):

    def __init__(self, file_name, file_path, paths, structure):

        super().__init__(file_name, file_path, paths)

        self.structure = structure

        self.dat_fields_map = {}
        self.txt_data = []

        pass

    def get_needle_groups(self):

        if "groups" in self.structure:
            return self.structure["groups"].split("|")
        else:
            return []

        pass

    def get_fields_map(self):

        return {
            "titles": self.structure["structure"]["titles"],
            "from": self.structure["structure"]["from"]
        }

        pass

    def set_dat_fields_map(self, fields_map):

        self.dat_fields_map = fields_map

        pass

    def parse(self):

        status_text = "Reading file: {}".format(self.get_name())
        self.callbacks["current_progress_text"](status_text)

        if self.source == "":
            return {
                "success": False,
                "error": "Can't read file data!"
            }

        txt_data = []

        rows = self.source.split("\n")
        del rows[0]
        del rows[0]
        del rows[0]

        total_rows = len(rows)
        percent = math.floor(total_rows / 100)
        count = 0
        for row in rows:
            if row == "":
                continue
            cells = row.split("\t")
            txt_data.append(cells)
            count += 1
            if count % percent == 0:
                self.callbacks["current_progress"](count / percent)

        self.callbacks["step_completed"]()

        return {
            "success": True,
            "data": txt_data
        }

        pass

    def build(self, dat_data):

        status_text = "Composing file: {}".format(self.get_name())
        self.callbacks["current_progress_text"](status_text)

        groups = self.get_needle_groups()
        total_rows = -1
        for group in groups:
            if group not in dat_data:
                return {
                    "success": False,
                    "error": "Insufficient data! Group '{}' is missing!".format(group)
                }
            if total_rows == -1:
                total_rows = len(dat_data[group])
            elif len(dat_data[group]) != total_rows:
                return {
                    "success": False,
                    "error": "Error composing TXT file! Groups with different rows count given!"
                }
        if total_rows < 0:
            return {
                "success": False,
                "error": "No data to writing!"
            }

        # progress
        percent = math.floor(total_rows / 100)

        # building
        result_data = []
        count = 0
        while count < total_rows:
            cells = []
            for field in self.structure["structure"]["fields"]:
                group = self.dat_fields_map[field["from"]]
                field_index = group["titles"].index(field["field"])
                cells.append(str(dat_data[field["from"]][count][field_index]))
            result_data.append(cells)

            count += 1
            if count % percent == 0:
                self.callbacks["current_progress"](count / percent)

        self.txt_data = result_data

        self.callbacks["step_completed"]()

        return {"success": True}

        pass

    def save(self):

        status_text = "Writing file: {}".format(self.get_name())
        self.callbacks["current_progress_text"](status_text)

        data = []

        header = self._build_header()
        for cells in header:
            row = "\t".join(cells)
            data.append(row)

        total_rows = len(self.txt_data)
        percent = math.floor(total_rows / 100)
        count = 0
        for cells in self.txt_data:
            row = "\t".join(cells)
            data.append(row)
            count += 1
            if count % percent == 0:
                self.callbacks["current_progress"](count / percent)

        data = "\n".join(data)

        if not self._write(data):
            return False

        self.callbacks["step_completed"]()

        return True

        pass

    def reset(self):

        self.source = ""
        self.txt_data = []
        self.dat_fields_map = {}

        pass

    def read(self):

        try:
            file = open(self.file_path, "r")
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

    # Private Methods

    def _build_header(self) -> list:

        row1 = []
        row2 = []
        row3 = []
        for field in self.structure["structure"]["fields"]:
            row1.append(field["title"])
            row2.append(field["from"])
            row3.append(self.dat_fields_map[field["from"]]["types"][field["field"]])

        return [row1, row2, row3]

        pass

    def _write(self, data):

        path = ROOT_PATH + "/" + self.paths["txt"] + "/" + self.structure["catalog_name"]
        if not os.path.isdir(path):
            os.makedirs(path)

        try:
            file = open(path + "/" + self.file_name, "w")
            file.write(data)
            file.close()
        except PermissionError:
            return False
        except FileNotFoundError:
            return False

        return True

        pass

    pass
