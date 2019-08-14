import abc
import subprocess

import jsonpatch

from drpy.fsm import logger
from drpy.models.machine import Machine


class BaseState(abc.ABC):

    def __init__(self, *args, api_client=None, machine=None, **kwargs):
        self.client = api_client
        self.machine = machine
        logger.info("Processing current state {}".format(str(self)))

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
            machine_uuid = agent_state.machine.Uuid
        machine_obj = agent_state.client.get(resource="machines/{}".format(
            machine_uuid
        ))
        return Machine(**machine_obj)
