import os

# get the newsest file
def newest(path=DEFAULT_DATA_DIRECTORY):
	files = os.listdir(path)
	paths = [os.path.join(path, basename) for basename in files]
	return max(paths, key=os.path.getctime)
