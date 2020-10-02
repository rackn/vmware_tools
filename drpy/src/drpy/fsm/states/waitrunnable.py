import asyncio
import copy
import logging

from drpy.api import wsclient
from drpy.exceptions import DRPException
from drpy.fsm.states.base import BaseState
from drpy.fsm.states.power import Exit, Reboot


class WaitRunnable(BaseState):
    def on_event(self, *args, **kwargs):
        agent_state = kwargs.get("agent_state")
        try:
            machine = self._get_machine(
                agent_state=agent_state,
                machine_uuid=agent_state.machine.Uuid
            )
        except DRPException:
            agent_state.failed = True
            return WaitRunnable(), agent_state

        if agent_state.machine.BootEnv != machine.BootEnv:
            # The boot env has changed. Time to reboot unless
            # we end in -install and then we exit
            if agent_state.machine.BootEnv.endswith("-install"):
                return Exit(), agent_state
            m_copy = copy.deepcopy(agent_state.machine)
            m_copy.Runnable = False
            self._patch_machine(
                agent_state,
                m_copy
            )
            return Reboot(), agent_state
        agent_state.machine = machine
        if machine.CurrentTask >= len(machine.Tasks):
            if agent_state.runner:
                return Exit(), agent_state
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                wsclient.wait_for_update(token=agent_state.config.token,
                                         uri=agent_state.config.endpoint,
                                         machine=agent_state.machine.Uuid
                                         )
            )
            return WaitRunnable(), agent_state
        if machine.Runnable:
            logging.debug("Machine Runnable. Checking context. {}".format(
                machine.Context))
            if machine.Context == "":
                from drpy.fsm.states.runtask import RunTask
                return RunTask(), agent_state
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            wsclient.wait_for_update(token=agent_state.config.token,
                                     uri=agent_state.config.endpoint,
                                     machine=agent_state.machine.Uuid
                                     )
        )
        return WaitRunnable(), agent_state
