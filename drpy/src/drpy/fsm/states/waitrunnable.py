import logging
import time

from drpy.fsm.states.base import BaseState
from drpy.fsm.states.power import Exit, Reboot


class WaitRunnable(BaseState):
    def on_event(self, *args, **kwargs):
        agent_state = kwargs.get("agent_state")
        machine = self._get_machine(
            agent_state=agent_state,
            machine_uuid=agent_state.machine.Uuid
        )
        if agent_state.machine.BootEnv != machine.BootEnv:
            # The boot env has changed. Time to reboot unless
            # we end in -install and then we exit
            if agent_state.machine.BootEnv.endswith("-install"):
                return Exit(), agent_state
            return Reboot(), agent_state
        agent_state.machine = machine
        if machine.CurrentTask >= len(machine.Tasks):
            if agent_state.runner:
                return Exit(), agent_state
            time.sleep(3)
            return WaitRunnable(), agent_state
        if machine.Runnable:
            logging.debug("Machine Runnable. Checking context. {}".format(
                machine.Context))
            if machine.Context == "":
                from drpy.fsm.states.runtask import RunTask
                return RunTask(), agent_state
        time.sleep(3)
        return WaitRunnable(), agent_state
