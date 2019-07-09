import abc
import subprocess

from drpy.fsm import logger


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
    def reboot(self):
        """

        :return:
        """
        ret = subprocess.call("reboot")
        if ret > 0:
            return "Failed to reboot."

    @staticmethod
    def power_off(self):
        ret = subprocess.call("poweroff")
        if ret > 0:
            return "Failed to poweroff"

    @property
    def state(self):
        return self.__class__.__name__
