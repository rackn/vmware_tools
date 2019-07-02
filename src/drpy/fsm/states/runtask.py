from drpy import action_runner
from drpy.api.client import Client
from drpy.models.job import Job, JobAction

from .base import BaseState


class RunTask(BaseState):

    def __init__(self, *args, api_client=None, prev_state=None, **kwargs):
        """

        :param args:
        :type api_client: Client
        :param api_client:
        :param prev_state:
        :param kwargs:
        """
        self.prev_state = prev_state
        self.job = None
        self.job_actions = []
        BaseState.__init__(self, *args, api_client=api_client, **kwargs)

    def on_event(self, event, *args, **kwargs):
        self.job = self._create_job()
        if not isinstance(self.job, Job):
            # todo: Handle the error
            pass
        self._set_job_status(status="running")
        self._get_job_actions()
        self._run_job_actions()
        self._set_job_status()
        return self._set_next_state()

    def _create_job(self):
        """

        :rtype: Job
        :return: Job or Error
        """
        job = Job()
        job.Machine = self.machine.Uuid
        j_obj = self.client.post_job(payload=job.__dict__)  # type: dict
        if "Error" in j_obj:
            # todo handle the error case
            pass
        return Job(**j_obj)

    def _set_job_status(self, status=None):
        raise NotImplementedError
        pass

    def _get_job_actions(self):
        jr = "jobs/{}/actions".format(self.job.Uuid)
        ja_list = self.client.get(resource=jr)
        for ja in ja_list:
            self.job_actions.append(JobAction(**ja))

    def _run_job_actions(self):
        results = []
        for action in self.job_actions:
            if action.Path != "":
                result = action_runner.add_file(job_action=action)
            else:
                result = action_runner.run_command(job_action=action)
            results.append(result)

    def _set_next_state(self):
        raise NotImplementedError
        return
