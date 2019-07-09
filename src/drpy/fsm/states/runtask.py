import copy

import jsonpatch

from drpy import action_runner
from drpy.models.job import Job, JobAction
from drpy.fsm.states.power import Exit
from .base import BaseState

from drpy.fsm import logger


class RunTask(BaseState):

    def on_event(self, *args, **kwargs):
        agent_state = kwargs.get("agent_state")
        if agent_state.machine.CurrentJob is None:
            logger.debug("Creating a new job for {}-{}".format(
                agent_state.machine.Name,
                agent_state.machine.Uuid
            ))
            agent_state.job = self._create_job(agent_state=agent_state)
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
        self._run_job_actions(agent_state=agent_state, actions=job_actions)
        logger.debug("Finished running Job Actions.")
        logger.debug("Setting Job State.")
        self._set_job_state(state="finished", agent_state=agent_state)
        return Exit(), agent_state

    def _create_job(self, agent_state=None):
        """

        :rtype: Job
        :return: Job or Error
        """
        job = Job()
        job.Machine = agent_state.machine.Uuid
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
        results = []
        for action in actions:
            if action.Path != "":
                logger.debug("Attempting to add a file to the file system.")
                try:
                    result = action_runner.add_file(job_action=action)
                    logger.debug("Added {} to the file system".format(
                        action.Path
                    ))
                except ValueError as ve:
                    result = {"Out": str(ve.value), "Exit_Code": -1}
                    agent_state.failed = True
                    logger.error("Failed to add file {}".format(
                        action.Path
                    ))
                    logger.exception(ve)
                except Exception as e:
                    result = {"Out": str(e.value), "Exit_Code": -1}
                    agent_state.failed = True
                    logger.error("Failed to add file {}".format(
                        action.Path
                    ))
                    logger.exception(e)
            else:
                logger.debug("Running command on system. {}".format(
                    action.Name
                ))
                result = action_runner.run_command(job_action=action)
                if result.get("Exit_Code") > 0 or result.get("Exit_Code") < 0:
                    # TODO: Handle the return codes for setting things
                    # up correctly. See taskRunner.go for the map
                    agent_state.failed = True
                    logger.error("Failed to run command on system.")

            results.append(result)

        return agent_state

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
