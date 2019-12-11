from drpy.fsm.states.base import BaseState

from drpy import logger


class Exit(BaseState):

    def on_event(self, *args, **kwargs):
        raise SystemExit


class Reboot(BaseState):

    def on_event(self, *args, **kwargs):
        agent_state = kwargs.get("agent_state")
        try:
            self.reboot()
        except Exception as e:
            logger.error("Reboot failed! {}".format(e.message))
        return Exit(), agent_state


class PowerOff(BaseState):

    def on_event(self, *args, **kwargs):
        agent_state = kwargs.get("agent_state")
        try:
            self.power_off()
        except Exception as e:
            logger.error("PowerOff failed! {}".format(e.message))
        return Exit(), agent_state
