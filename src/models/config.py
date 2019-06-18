import configparser
from collections import namedtuple

from cli.cli import verify_conf_file


# Config element types: [endpoint: str, token: str, machine_uuid: uuid.UUID]
Config = namedtuple("Config", ["endpoint", "token", "machine_uuid"])
Config.__new__.__defaults__ = (None, None, None)


class ConfigException(Exception):
    """A config error has occurred."""


def parse(conf_file=None):
    """
    Given a full path to a config file return a Config object

    :type conf_file: str
    :param conf_file: full path to the config file
    :rtype: Config
    :return: Config object
    """
    if verify_conf_file(conf_file):
        conf = configparser.ConfigParser()
        conf.read(conf_file)
        if conf.has_section('Config'):
            conf_dict = dict(conf.items('Config'))
            ep = conf_dict['endpoint']
            tkn = conf_dict['token']
            m_uuid = conf_dict['machine_uuid']
            return Config(endpoint=ep, token=tkn, machine_uuid=m_uuid)
        else:
            raise ConfigException('{} missing [Config] section.'.format(
                conf_file))
    else:
        raise ConfigException('Unable to read {}'.format(conf_file))
