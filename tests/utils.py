import pytest
import os

from TimeCsv import DataFile


FAKE_DATA_PATH = os.path.join(
	os.path.dirname(__file__),
	"fake_data.csv"
)

NUM_ENTRIES = 4

@pytest.fixture
def data_file():
	return DataFile(FAKE_DATA_PATH)

@pytest.fixture
def df(data_file):
	return data_file.to_dataframe()
