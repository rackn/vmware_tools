import configparser
import datetime
import os
import shutil
from collections import namedtuple

from drpy.cli.cli import verify_conf_file
from drpy.cli.cli import get_volumes


# Config element types: [endpoint: str, token: str, machine_uuid: uuid.UUID]
Config = namedtuple("Config", [
    "endpoint",
    "token",
    "machine_uuid",
    "command_timeout",
    "command_path",
    "machine_wait",
    "duration",
    "last_updated",
    "never_update_token"
])

Config.__new__.__defaults__ = (
    None,
    None,
    None,
    None,
    None,
    "wait=10m",
    "60",
    None,
    False
)


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
            mw = conf_dict.get("machine_wait", "wait=10m")
            dur = conf_dict.get("duration", "60")
            las = datetime.datetime.now()
            up_tok = conf_dict.get("never_update_token", False)
            return Config(
                endpoint=ep,
                token=tkn,
                machine_uuid=m_uuid,
                machine_wait=mw,
                duration=dur,
                last_updated=las,
                never_update_token=up_tok
            )
        else:
            raise ConfigException('{} missing [Config] section.'.format(
                conf_file))
    else:
        raise ConfigException('Unable to read {}'.format(conf_file))


def update(replace=None, path=None):
    """
    Update the config file at a given path with the values set in the
    replace dict. This currently only works on the "Config" section

    This updates the conf file on the file system. Then returns the
    updated config object.

    :param replace:
    :param path:
    :return:
    """
    conf_file = path + "/rackn/drpy.conf"
    if not verify_conf_file(conf_file):
        copy(dest=path)
        if not verify_conf_file(conf_file):
            raise ConfigException('Unable to read {}'.format(conf_file))
    # read in the existing config to make sure we get the logging as well
    conf = configparser.ConfigParser()
    conf.read(conf_file)
    # taking the conf dict find the "Config" section and update the existing
    # values with the new ones
    items = conf.items("Config")
    for key, val in items:
        if key in replace.keys():
            conf.set("Config", key, replace[key])
    with open(conf_file, "w+") as f:
        conf.write(f)
    return parse(conf_file)


def copy(dest=None):
    """
    Given a dest path look up all the vfats, then remove
    the dest from the vfat list since it doesnt have a conf
    next pick a volume to copy the config from

    :param dest:
    :return:
    """
    ending = "/rackn/drpy.conf"
    vfats = get_volumes(vol_filter='vfat')
    vfat_confs = [x + ending for x in vfats]
    if dest + ending in vfat_confs:
        vfat_confs.remove(dest+ending)
    if not os.path.isdir(dest + "/rackn"):
        os.mkdir(dest + "/rackn")
    shutil.copy(vfat_confs[0], dest + ending)
