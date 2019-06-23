import copy

import jsonpatch

from tests.api import my_vcr

from drpy.api.client import Client
from drpy.models.machine import Machine
from drpy.models.job import Job


@my_vcr.use_cassette('get_machine.yaml')
def test_get_machine():
    client = Client(endpoint="https://192.168.1.53:8092/")
    client.setup_basic_auth("rocketskates", "passthis")
    objs = client.get("machines/6d109287-dffa-4344-a727-2b17970ca210")
    machine = Machine(**objs)
    assert machine.Uuid == "6d109287-dffa-4344-a727-2b17970ca210"


@my_vcr.use_cassette('get_job.yaml')
def test_get_job():
    client = Client(endpoint="https://192.168.1.53:8092/")
    client.setup_basic_auth("rocketskates", "passthis")
    objs = client.get("jobs/00d6b39e-3e1d-4836-b697-79054f9d6ff4")
    job = Job(**objs)
    assert job.State == "finished"


@my_vcr.use_cassette('patch_machine_runnable_field.yaml')
def test_patch_machine_runnable_field():
    client = Client(endpoint="https://192.168.1.53:8092/")
    client.setup_basic_auth("rocketskates", "passthis")
    objs = client.get("machines/6d109287-dffa-4344-a727-2b17970ca210")

    m = Machine(**objs)
    m_tmp = copy.deepcopy(m)
    m_tmp.Runnable = True
    m_patch = jsonpatch.make_patch(m.__dict__, m_tmp.__dict__)
    m1obj = client.patch(resource="machines/6d109287-dffa-4344-a727-2b17970ca210",
                         payload=m_patch.to_string())
    m1 = Machine(**m1obj)
    assert m1 == m_tmp
