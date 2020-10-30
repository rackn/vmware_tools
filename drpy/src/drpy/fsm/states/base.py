import abc
import copy
import json
import subprocess
import urllib

from http.client import RemoteDisconnected

import jsonpatch

from drpy.exceptions import DRPException
from drpy.models.job import Job
from drpy.fsm import logger
from drpy.models.machine import Machine


class BaseState(abc.ABC):

    def __init__(self, *args, api_client=None, machine=None, **kwargs):
        self.client = api_client
        self.machine = machine
        logger.debug("Processing current state {}".format(str(self)))

    @abc.abstractmethod
    def on_event(self, *args, **kwargs):
        """
        Handle events that are passed to this state.

        :param event:
        :return:
        """
        raise NotImplementedError

    def __repr__(self):
        """
        Leverage the __str__ method to describe the state.

        :return:
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the state

        :return:
        """
        return self.__class__.__name__

    @staticmethod
    def reboot():
        """

        :return:
        """
        ret = subprocess.call("reboot")
        if ret > 0:
            return "Failed to reboot."

    @staticmethod
    def power_off():
        ret = subprocess.call("poweroff")
        if ret > 0:
            return "Failed to poweroff"

    @property
    def state(self):
        return self.__class__.__name__

    def _patch_machine(self, agent_state=None, machine_copy=None):
        m_patch = jsonpatch.make_patch(
            agent_state.machine.__dict__,
            machine_copy.__dict__
        )
        machine_obj = agent_state.client.patch(
            resource="machines/{}".format(agent_state.machine.Uuid),
            payload=m_patch.to_string()
        )
        return Machine(**machine_obj)

    def _get_machine(self, agent_state=None, machine_uuid=None):
        if machine_uuid is None:
            logger.debug("machine_uuid was none.")
            machine_uuid = agent_state.machine.Uuid
        try:
            logger.debug("Making base request to fetch machine.")
            machine_obj = agent_state.client.get(resource="machines/{}".format(
                machine_uuid
            ))
            return Machine(**machine_obj)
        except (urllib.error.URLError, RemoteDisconnected) as e:
            logger.error("Failed to get Machine object {}".format(
                machine_uuid), e)
            raise DRPException("Failed to get Machine Object.")

    def _set_machine_current_job_state(self, state=None, agent_state=None):
        state = state
        logger.debug("Setting Machine {} || CurrentJob: {} || "
                     "To state: {}".format(agent_state.machine.Uuid,
                                           agent_state.machine.CurrentJob,
                                           state))
        states = ["created", "running", "failed", "finished", "incomplete"]
        if state not in states:
            raise NotImplementedError
        payload = [{"op": "replace", "path": "/State", "value": state}]
        payload = json.dumps(payload)
        resource = "jobs/{}".format(agent_state.machine.CurrentJob)
        agent_state.client.patch(
            resource=resource,
            payload=payload
        )

    def _set_job_state(self, state=None, agent_state=None):
        state = state
        if agent_state.failed:
            state = "failed"
        elif agent_state.incomplete:
            state = "incomplete"
        logger.debug("Setting Job {} to State {}".format(
            agent_state.job.Uuid,
            state
        ))
        states = ["created", "running", "failed", "finished", "incomplete"]
        if state not in states:
            raise NotImplementedError
        job_copy = copy.deepcopy(agent_state.job)  # type: Job
        job_copy.State = state
        job_diff = jsonpatch.make_patch(
            agent_state.job.__dict__,
            job_copy.__dict__
        )
        resource = "jobs/{}".format(agent_state.job.Uuid)
        job_res = agent_state.client.patch(
            resource=resource,
            payload=job_diff.to_string()
        )
        new_job = Job(**job_res)
        agent_state.job = new_job
        return agent_state

    def _get_job(self, agent_state=None):
        jr = "jobs/{}".format(
            agent_state.machine.CurrentJob
        )
        logger.debug("Fetching job resource for job id {}".format(
            agent_state.machine.CurrentJob
        ))
        job_obj = agent_state.client.get(
            resource=jr
        )
        return Job(**job_obj)
