import os

from ..utils.consts import *
from ..parsing.parsing import DataFile, DataFolder

def _open_file(file_path: str):
	if os.path.exists(file_path):
		if os.path.isfile(file_path):
			return DataFile(file_path)
		if os.path.isdir(file_path):
			return DataFolder(file_path)

	for extension in POSSIBLE_FILE_EXTENSIONS:
		path = file_path + extension
		if os.path.exists(path) and os.path.isfile(path):
			return DataFile(path)

	return None

def open_data_file(file_path: str):
	file_path = os.path.expanduser(file_path)

	for path in (
		file_path,
		os.path.join(os.getcwd(), file_path),
		os.path.join(DEFAULT_DATA_DIRECTORY, file_path)
	):
		if (result := _open_file(path)) is not None:
			return result

	raise ValueError(f"file/folder not found: {file_path}")
