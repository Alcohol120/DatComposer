from .File import File
import math


class TXTFile(File):

    def __init__(self, file_name, file_path, structure):

        super().__init__(file_name, file_path)

        self.structure = structure

        pass

    def get_needle_groups(self):

        if "groups" in self.structure:
            return self.structure["groups"].split("|")
        else:
            return []

        pass

    def build(self, dat_data, fields_map):

        status_text = "Writing file: {}".format(self.get_name())
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
                group = fields_map[field["from"]]
                field_index = group.index(field["field"])
                cells.append(dat_data[field["from"]][count][field_index])
            result_data.append(cells)

            count += 1
            if count % percent == 0:
                self.callbacks["current_progress"](count / percent)

        self.callbacks["step_completed"]()

        return {
            "success": True,
            "data": result_data
        }

        pass

    # Private Methods

    pass
