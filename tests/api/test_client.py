import copy

import jsonpatch

from tests.api import my_vcr

from drpy.models.machine import Machine
from drpy.models.job import Job


@my_vcr.use_cassette('get_machine.yaml')
def test_get_machine(setup_client):
    client = setup_client
    objs = client.get("machines/6d109287-dffa-4344-a727-2b17970ca210")
    machine = Machine(**objs)
    assert machine.Uuid == "6d109287-dffa-4344-a727-2b17970ca210"


@my_vcr.use_cassette('get_job.yaml')
def test_get_job(setup_client):
    client = setup_client
    objs = client.get("jobs/00d6b39e-3e1d-4836-b697-79054f9d6ff4")
    job = Job(**objs)
    assert job.State == "finished"


@my_vcr.use_cassette('patch_machine_runnable_field.yaml')
def test_patch_machine_runnable_field(setup_client):
    client = setup_client
    objs = client.get("machines/6d109287-dffa-4344-a727-2b17970ca210")

    m = Machine(**objs)
    m_tmp = copy.deepcopy(m)
    m_tmp.Runnable = True
    m_patch = jsonpatch.make_patch(m.__dict__, m_tmp.__dict__)
    m1obj = client.patch(
        resource="machines/6d109287-dffa-4344-a727-2b17970ca210",
        payload=m_patch.to_string())
    m1 = Machine(**m1obj)
    assert m1 == m_tmp


@my_vcr.use_cassette("post_job_conflict.yaml")
def test_post_job_gets_409(setup_client):
    my_machine = "e5bae439-d306-4dcc-9b78-32a0cbc231be"
    j = Job()
    j.Machine = my_machine
    client = setup_client
    job_obj = client.post_job(j.__dict__)
    assert job_obj['Error'] == 409


@my_vcr.use_cassette("post_job_success.yaml")
def test_post_job_success(setup_client):
    my_machine = "f45fbc79-4081-4f27-86e4-bbf9d3757fd4"
    j = Job()
    j.Machine = my_machine
    client = setup_client
    job_obj = client.post_job(j.__dict__)
    j2 = Job(**job_obj)
    assert j.Machine == j2.Machine
