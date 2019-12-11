from drpy.models.base import Namespace


class AgentState(Namespace):

    attrs = [
        "wait",
        "failed",
        "incomplete",
        "reboot",
        "poweroff",
        "stop",
        "client",
        "job",
        "machine",
        "task",
        "config",
        "runner"
    ]
