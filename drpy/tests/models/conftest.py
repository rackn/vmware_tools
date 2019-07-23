import os
import pytest


@pytest.fixture()
def get_dir_path():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path += "/../fixtures/"
    return dir_path
