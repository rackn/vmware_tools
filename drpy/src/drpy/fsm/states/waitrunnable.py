import time

from drpy.fsm.states.base import BaseState
from drpy.fsm.states.runtask import RunTask


class WaitRunnable(BaseState):
    def on_event(self, *args, **kwargs):
        agent_state = kwargs.get("agent_state")
        machine = self._get_machine(
            agent_state=agent_state,
            machine_uuid=agent_state.machine.Uuid
        )
        if machine.Runnable:
            agent_state.machine = machine
            return RunTask(), agent_state
        time.sleep(3)
        return WaitRunnable(), agent_state
