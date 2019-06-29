import pytest

from drpy import action_runner
from drpy.exceptions import DRPException
from drpy.models.job import JobAction


# Be sure the first item in this list is an empty
# string
testdata = [
    "",
    12345,
    {"a": 1},
    [1, 2, 3]
]


@pytest.mark.parametrize("job_action", testdata)
def test_run_command_called_with_wrong_types_raises_valueerror(job_action):
    """
    Testing to make sure we raise a value error when called and not using
    a valid JobAction object.
    """
    with pytest.raises(ValueError):
        action_runner.run_command(job_action)


def test_run_command_raises_drpexception_when_ja_contains_path():
    """
    Run command should only work when a Path is not set. If a Path
    is set then you should be using add_file and placing Contents
    at Path.
    """
    ja = JobAction(Path="/foo/bar/baz")
    with pytest.raises(DRPException) as dre:
        action_runner.run_command(ja)
    assert str(dre.value) == "run_command called when path provided."


@pytest.mark.parametrize("job_action", testdata)
def test_add_file_called_with_wrong_types_raises_valueerror(job_action):
    """
    Testing to make sure we raise a value error when called not using
    a valid JobAction
    """
    with pytest.raises(ValueError):
        action_runner.add_file(job_action)


@pytest.mark.parametrize("job_action", testdata[1:])
def test_add_file_called_with_wrong_types_in_path_raise_exception(job_action):
    """
    Testing to make sure if Path is not a str then we raise ValueError
    """
    ja = JobAction(Path=job_action)
    with pytest.raises(ValueError):
        action_runner.add_file(ja)
