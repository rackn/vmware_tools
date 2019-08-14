import copy

from drpy.fsm.states.base import BaseState
from drpy.fsm.states.runtask import RunTask

from drpy import logger


class Initialize(BaseState):

    def on_event(self, *args, **kwargs):
        agent_state = kwargs.get("agent_state")
        machine_uuid = kwargs.get("machine_uuid")
        logger.debug("Fetching machine: {}".format(
            machine_uuid
        ))
        agent_state.machine = self._get_machine(
            agent_state=agent_state,
            machine_uuid=machine_uuid
        )
        logger.debug("Retrieved machine: {}-{}".format(
            agent_state.machine.Name,
            agent_state.machine.Uuid
        ))
        if not agent_state.machine.Runnable:
            logger.debug("Machine not runnable. Patching.")
            m_copy = copy.deepcopy(agent_state.machine)
            m_copy.Runnable = True
            agent_state.machine = self._patch_machine(agent_state, m_copy)
            logger.debug("Successfully Patched machine to runnable")

        return RunTask(), agent_state

    def _set_job_running(self, agent_state=None):
        pass
