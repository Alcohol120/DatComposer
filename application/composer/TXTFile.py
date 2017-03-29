from .File import File
import math


class TXTFile(File):

    def __init__(self, file_name, file_path, paths, structure):

        super().__init__(file_name, file_path, paths)

        self.read_mode = "r"
        self.write_mode = "w"

        self.source = ""
        self.output = ""

        self.structure = structure
        self.group_aliases = self._get_groups_aliases()

        self.dat_fields_map = {}

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
        if percent < 1:
            percent = 1
        count = 0
        for row in rows:
            if self.canceled:
                self.canceled = False
                return {
                    "success": False,
                    "error": "Operation canceled by user!"
                }
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

        status_text = "Writing file: {}".format(self.get_name())
        self.callbacks["current_progress_text"](status_text)

        groups = self.get_needle_groups()
        rows = self._get_total_rows(groups, dat_data)
        if not rows["success"]:
            return rows
        else:
            total_rows = rows["total_rows"]

        # progress
        percent = math.floor(total_rows / 100)
        if percent < 1:
            percent = 1

        rows = []

        # header
        header = self._build_header()
        for cells in header:
            row = "\t".join(cells)
            rows.append(row)

        # building
        count = 0
        while count < total_rows:
            cells = []
            for field in self.structure["structure"]["fields"]:
                if self.canceled:
                    self.canceled = False
                    return {
                        "success": False,
                        "error": "Operation canceled by user!"
                    }
                group_name = field["from"]
                if group_name not in self.dat_fields_map:
                    group_name = self.group_aliases[group_name]
                group = self.dat_fields_map[group_name]
                field_index = group["titles"].index(field["field"])
                cells.append(str(dat_data[group_name][count][field_index]))
            rows.append("\t".join(cells))

            count += 1
            if count % percent == 0:
                self.callbacks["current_progress"](count / percent)

        self.output = "\n".join(rows)
        self.callbacks["step_completed"]()

        return {"success": True}

        pass

    def reset(self):

        self.canceled = False
        self.source = ""
        self.output = ""
        self.dat_fields_map = {}

        pass

    # Private Methods

    def _get_groups_aliases(self):

        if "groups" not in self.structure or type(self.structure["groups"]) is not str:
            return {}

        aliases = {}
        groups = self.structure["groups"].split("|")
        for group in groups:
            names = group.split(":")
            if len(names) > 1:
                aliases[names[1]] = names[0]

        return aliases

        pass

    def _build_header(self) -> list:

        row1 = []
        row2 = []
        row3 = []
        for field in self.structure["structure"]["fields"]:
            group_name = field["from"]
            if field["from"] not in self.dat_fields_map:
                group_name = self.group_aliases[field["from"]]
            row1.append(field["title"])
            row2.append(group_name)
            row3.append(self.dat_fields_map[group_name]["types"][field["field"]])

        return [row1, row2, row3]

        pass

    @staticmethod
    def _get_total_rows(groups, dat_data):

        total_rows = -1
        for group in groups:
            group = group.split(":")
            if group[0] not in dat_data:
                return {
                    "success": False,
                    "error": "Insufficient data! Group '{}' is missing!".format(group[0])
                }
            if total_rows == -1:
                total_rows = len(dat_data[group[0]])
            elif len(dat_data[group[0]]) != total_rows:
                return {
                    "success": False,
                    "error": "Error composing TXT file! Groups with different rows count given!"
                }
        if total_rows < 0:
            return {
                "success": False,
                "error": "No data to writing!"
            }
        else:
            return {
                "success": True,
                "total_rows": total_rows
            }

        pass

    pass
