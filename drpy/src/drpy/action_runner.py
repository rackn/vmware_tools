import os
import subprocess

from drpy.exceptions import DRPException
from drpy.models.job import JobAction


def run_command(job_action=None, timeout=None, expath=None):
    """
    executes a shell script using /bin/sh. If Path is not
    an empty string DRPException is raised. The shell script
    is passed in as STDIN. All stdout and any errors along with
    the return code will be returned in a dict.

    :type job_action: JobAction
    :param job_action:
    :type timeout: int
    :param timeout:
    :type expath: str
    :param expath: Full path for where to write & execute scripts.
    :return:
    """
    if not isinstance(job_action, JobAction):
        raise ValueError("unexpected object type passed as job_action")
    if job_action.Path != '':
        raise DRPException("run_command called when path provided.")
    command = job_action.Content
    path = expath
    if path is None or path != '':
        path = "/opt/rackn/runner"
    if path.endswith("/"):
        path = path[:-1]
    os.makedirs(path, exist_ok=True)
    file = path + "/{}".format(job_action.Name)
    with open(file, 'x') as f:
        f.writelines(command)
    os.chmod(file, 0o700)
    cpobj = subprocess.run(
        file,
        timeout=timeout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    os.unlink(file)
    return {
        "Out": cpobj.stdout,
        "Errors": cpobj.stderr,
        "Exit_Code": cpobj.returncode
    }


def add_file(job_action=None):
    """
    Given a JobAction place the Contents on the file system
    in the Path

    :type job_action: JobAction
    :param job_action:
    :return:
    """
    if not isinstance(job_action, JobAction):
        raise ValueError("Unexpected object type passed as job_action")
    file = job_action.Path
    if file == '':
        raise ValueError("add_file called with no path provided.")
    if not isinstance(file, str):
        raise ValueError("file path info not a string.")
    dir_path = os.path.dirname(file)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file, "w") as f:
        f.write(job_action.Content)
