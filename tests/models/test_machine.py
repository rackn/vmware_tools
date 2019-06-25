import json

from drpy.models.machine import Machine


def test_json_to_machine(get_dir_path):
    dir_path = get_dir_path
    json_file = dir_path + "machine.json"
    with open(json_file, "r") as jf:
        data = jf.read()
    json_data = json.loads(data)
    m = Machine(**json_data)
    assert m.Name == "dd0-67-e5-4d-b2-3f.mrice.internal"
    assert isinstance(m.Meta, dict)
