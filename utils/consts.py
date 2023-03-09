import os

MAIN_FOLDER = os.path.dirname(os.path.dirname(__file__))
DEFAULT_DATA_DIRECTORY   = os.path.join(MAIN_FOLDER, "data")

POSSIBLE_FILE_EXTENSIONS = [".tcsv", ".csv", ".txt", ""]
