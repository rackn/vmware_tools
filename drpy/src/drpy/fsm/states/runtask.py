import copy

import jsonpatch

from drpy import action_runner
from drpy.api.client import Client
from drpy.models.job import Job, JobAction
from drpy.fsm.states.power import Exit, Reboot, PowerOff
from .base import BaseState

from drpy import logger


class RunTask(BaseState):

    def on_event(self, *args, **kwargs):
        agent_state = kwargs.get("agent_state")
        if agent_state.machine.CurrentJob == "":
            logger.debug("Creating a new job for {}-{}".format(
                agent_state.machine.Name,
                agent_state.machine.Uuid
            ))
            agent_state.job = self._create_job(agent_state=agent_state)
            if agent_state.job.Uuid is None:
                return Exit(), agent_state
            logger.debug("Successfully created job {}".format(
                agent_state.job.Uuid
            ))
        else:
            logger.debug("Existing Job {} for {}-{}".format(
                agent_state.machine.CurrentJob,
                agent_state.machine.Name,
                agent_state.machine.Uuid
            ))
            logger.debug("Loading copy of Job into agent_state")
            agent_state.job = self._get_job(agent_state=agent_state)
            logger.debug("Current job state: {}".format(
                agent_state.job.State
            ))
            if agent_state.job.State == "finished":
                agent_state.job = self._create_job(agent_state=agent_state)
                logger.debug("New Job contents: {}".format(
                    agent_state.job.__dict__
                ))
                if agent_state.job.Uuid == "" or agent_state.job.Uuid is None:
                    logger.debug("No more jobs to process.")
                    return Exit(), agent_state
        if agent_state.job.State != "running":
            logger.debug("Setting job {} to state running from {}".format(
                agent_state.job.Uuid,
                agent_state.job.State
            ))
            agent_state = self._set_job_state(
                agent_state=agent_state,
                state="running"
            )
        logger.debug("Fetching job actions for job {}".format(
            agent_state.job.Uuid
        ))
        job_actions = self._get_job_actions(agent_state=agent_state)
        agent_state, action_results = self._run_job_actions(
            agent_state=agent_state,
            actions=job_actions
        )
        logger.debug("Finished running Job Actions.")
        logger.debug("Setting Job State.")
        agent_state = self._set_job_state(
            state="finished",
            agent_state=agent_state
        )
        return self._handle_state(
            agent_state=agent_state,
            action_results=action_results
        )

    def _create_job(self, agent_state=None):
        """

        :rtype: Job
        :return: Job or Error
        """
        logger.debug("Creating job for {}".format(
            agent_state.machine.Uuid
        ))
        job = Job()
        job.Machine = agent_state.machine.Uuid
        logger.debug("POSTing {}".format(
            job.__dict__
        ))
        j_obj = agent_state.client.post_job(payload=job.__dict__)  # type: dict
        if "Error" in j_obj:
            # todo handle the error case
            logger.error("Error in j_obj for create_job. {}".format(
                j_obj
            ))
            pass
        return Job(**j_obj)

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

    def _get_job_actions(self, agent_state=None):
        jr = "jobs/{}/actions".format(agent_state.job.Uuid)
        ja_list = agent_state.client.get(resource=jr)
        logger.debug("Successfully retrieved {} job actions for job {}".format(
            len(ja_list),
            agent_state.job.Uuid
        ))
        job_actions = []
        for ja in ja_list:
            job_actions.append(JobAction(**ja))
        return job_actions

    def _run_job_actions(self, agent_state=None, actions=None):
        for action in actions:
            agent_state.stop = False
            agent_state.poweroff = False
            agent_state.reboot = False
            agent_state.incomplete = False
            agent_state.failed = False
            if action.Path != "":
                logger.debug("Attempting to add a file to the file system.")
                try:
                    action_runner.add_file(job_action=action)
                    log_msg = "Added {} to the file system".format(action.Path)
                    logger.debug(log_msg)
                    c = agent_state.client  # type: Client
                    c.put_job_log(job=agent_state.job.Uuid, log_msg=log_msg)
                except Exception as e:
                    agent_state.failed = True
                    log_msg = "Failed to add file {}".format(action.Path)
                    logger.error(log_msg)
                    m_copy = copy.deepcopy(agent_state.machine)
                    m_copy.Runnable = False
                    self._patch_machine(
                        agent_state,
                        m_copy
                    )
                    logger.exception(e)
                    c = agent_state.client  # type: Client
                    log_msg += "\n"
                    log_msg += repr(e)
                    c.put_job_log(job=agent_state.job.Uuid, log_msg=log_msg)
                    return agent_state, -1
            else:
                logger.debug("Running command on system. {}".format(
                    action.Name
                ))
                result = action_runner.run_command(
                    job_action=action,
                    timeout=agent_state.config.command_timeout,
                    expath=agent_state.config.command_path
                )
                if result.get("Exit_Code") != 0:
                    agent_state.failed = True
                    log_msg = "Failed to run command on system."
                    logger.error(log_msg)
                    m_copy = copy.deepcopy(agent_state.machine)
                    m_copy.Runnable = False
                    self._patch_machine(
                        agent_state,
                        m_copy
                    )
                    code = int(result.get("Exit_Code"))
                    c = agent_state.client  # type: Client
                    log_msg = "Command: {}\n{}".format(
                        action.Name,
                        result.get("Errors")
                    )
                    log_msg += "\nExit Code: {}".format(code)
                    c.put_job_log(job=agent_state.job.Uuid, log_msg=log_msg)
                    if code == 16:
                        agent_state.stop = True
                        agent_state.failed = False
                    elif code == 32:
                        agent_state.poweroff = True
                        agent_state.failed = False
                    elif code == 64:
                        agent_state.reboot = True
                        agent_state.failed = False
                    elif code == 128:
                        agent_state.incomplete = True
                        agent_state.failed = False
                    elif code == 144:
                        agent_state.stop = True
                        agent_state.incomplete = True
                        agent_state.failed = False
                    elif code == 160:
                        agent_state.incomplete = True
                        agent_state.poweroff = True
                        agent_state.failed = False
                    elif code == 192:
                        agent_state.incomplete = True
                        agent_state.reboot = True
                        agent_state.failed = False
                    return agent_state, code
        return agent_state, None

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

    def _handle_state(self, agent_state=None, action_results=None):
        if action_results is None:
            return RunTask(), agent_state
        if agent_state.failed:
            from drpy.fsm.states.waitrunnable import WaitRunnable
            return WaitRunnable(), agent_state
        if agent_state.reboot:
            return Reboot(), agent_state
        if agent_state.poweroff:
            return PowerOff(), agent_state
        if agent_state.stop:
            return Exit(), agent_state
