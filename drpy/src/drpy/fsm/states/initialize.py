import copy

from drpy.exceptions import DRPExitException
from drpy.fsm.states.base import BaseState
from drpy.fsm.states.power import Exit
from drpy.fsm.states.waitrunnable import WaitRunnable


from drpy import logger


class Initialize(BaseState):

    def on_event(self, *args, **kwargs):
        agent_state = kwargs.get("agent_state")
        machine_uuid = kwargs.get("machine_uuid")
        logger.debug("Fetching machine: {}".format(
            machine_uuid
        ))
        try:
            agent_state.machine = self._get_machine(
                agent_state=agent_state,
                machine_uuid=machine_uuid
            )
        except DRPExitException:
            return Exit(), agent_state
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

        if agent_state.machine.CurrentJob != "":
            logger.debug("Existing Job {} for {}-{}".format(
                agent_state.machine.CurrentJob,
                agent_state.machine.Name,
                agent_state.machine.Uuid
            ))
            logger.debug("Loading copy of Job into agent_state")
            try:
                agent_state.job = self._get_job(agent_state=agent_state)
                logger.debug("Current job state: {}".format(
                    agent_state.job.State
                ))
                if (agent_state.job.State == "running" or
                        agent_state.job.State == "created"):
                    agent_state = self._set_job_state(
                        state="failed",
                        agent_state=agent_state
                    )
                    logger.debug("Current Job closed on startup: {}".format(
                        agent_state.__dict__
                    ))
            except Exception as e:
                logger.debug(e.message)
                logger.debug("Current Job is not present: {}".format(
                    agent_state.machine.CurrentJob))
        logger.debug("Setting Etag back to 0 from Initialize -> WaitRunnable")
        agent_state.client.machine_etag_header = {'If-None-Match': 0}
        return WaitRunnable(), agent_state

    def _set_job_running(self, agent_state=None):
        pass
