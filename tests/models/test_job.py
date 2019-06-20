import json
import os

from models.job import Job


def test_json_to_job():
    machine = "24beda27-9118-4ebb-9dd6-af5f94bf6ed7"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    json_file = dir_path + "/../fixtures/job.json"
    with open(json_file, "r") as jf:
        data = jf.read()
    json_data = json.loads(data)
    job = Job(**json_data)
    assert job.Machine == machine
