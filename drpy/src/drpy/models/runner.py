from drpy.models.base import Namespace


class AgentState(Namespace):

    attrs = [
        "failed",
        "incomplete",
        "reboot",
        "poweroff",
        "stop",
        "client",
        "job",
        "machine",
        "task",
        "config"
    ]
