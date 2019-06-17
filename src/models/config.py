from collections import namedtuple

# Config element types: [endpoint: str, token: str, machine_uuid: uuid.UUID]
Config = namedtuple("Config", ["endpoint", "token", "machine_uuid"])
Config.__new__.__defaults__ = (None, None, None)


class ConfigException(Exception):
    """A config error has occurred."""


