import os

# path settings
ROOT_PATH = os.getcwd().replace("\\", "/")


# path regex
DIR_NAME_RE = "^([a-zA-Z0-9_\- .]+/)*[a-zA-Z0-9_\- .]+$"
FILENAME_RE = "^[a-zA-Z0-9_\-.\[\]()]+$"
FILE_EXT_RE = lambda ext: "^[a-zA-Z0-9_\-.\[\]()]+\.{}$".format(ext)
FILE_PATH_RE = lambda ext: "^([a-zA-Z0-9_\- .]+/)*[a-zA-Z0-9_\-.\[\]()]+\.[a-zA-Z]+$"
FILE_PATH_EXT_RE = lambda ext: "^([a-zA-Z0-9_\- .]+/)*[a-zA-Z0-9_\-.\[\]()]+\.{}$".format(ext)
