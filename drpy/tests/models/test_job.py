import json

from drpy.models.job import Job
from drpy.models.job import JobAction


def test_json_to_job(get_dir_path):
    machine = "24beda27-9118-4ebb-9dd6-af5f94bf6ed7"
    dir_path = get_dir_path
    json_file = dir_path + "job.json"
    with open(json_file, "r") as jf:
        data = jf.read()
    json_data = json.loads(data)
    job = Job(**json_data)
    assert job.Machine == machine


def test_json_to_job_action(get_dir_path):
    dir_path = get_dir_path
    json_file = dir_path + "job_actions.json"
    ja_list = []
    with open(json_file, "r") as jf:
        data = jf.read()
    json_data = json.loads(data)
    for item in json_data:
        ja = JobAction(**item)
        ja_list.append(ja)

    assert len(ja_list) == 1
    assert ja_list[0].Name == "enforce-sledgehammer"
    assert ja_list[0].Path == ''
