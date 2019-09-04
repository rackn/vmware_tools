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
        except:
            logger.debug("Reboot failed!\n")
        return Exit(), agent_state


class PowerOff(BaseState):

    def on_event(self, *args, **kwargs):
        agent_state = kwargs.get("agent_state")
        try:
            self.power_off()
        except:
            logger.debug("PowerOff failed!\n")
        return Exit(), agent_state
