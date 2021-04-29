import argparse
import json
import os
import subprocess


__author__ = "RackN"


def build_arg_parser():
    """
    Builds a standard arg parser to pass in opts
    for starting the agent

    :rtype: argparse.ArgumentParser
    :return: The argument parser
    """
    parser = argparse.ArgumentParser(
        description="Standard Args For Starting DRPY"
    )
    parser.add_argument(
        "-f",
        "--conf_file",
        required=True,
        action='store',
        help="Location of config file"
    )
    parser.add_argument(
        "-r",
        "--runner",
        help="Single runner mode. Does not function as long lived agent.",
        action="store_true"
    )
    return parser


def verify_conf_file(file_loc=None):
    """
    Verify that the provided file_loc exists and
    is readable

    :type file_loc: str
    :param file_loc: full path to the config file
    :rtype: boolean
    :return: True or False
    """
    if os.path.isfile(file_loc):
        return os.access(file_loc, os.R_OK)
    else:
        return False


def get_volumes(vol_filter=None):
    """
    Return a list of volumes as reported by localcli storage subsystem
    Takes optional filter which can be
    vmfs, vfat, or nfs. Other values will be ignored.

    :return:
    """
    outobj = subprocess.run(
        "localcli --formatter json storage filesystem list",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True,
    )
    file_list = json.loads(outobj.stdout)
    if vol_filter is not None:
        vol_filter = vol_filter.lower()
        if vol_filter == 'vmfs':
            file_list = [i['Mount Point'] for i in file_list
                         if i['Type'].lower() == 'VFFS' or
                         'vmfs' in i['Type'].lower()]
        elif vol_filter == 'vfat':
            file_list = [i['Mount Point'] for i in file_list
                         if 'vfat' in i['Type'].lower()]
        elif vol_filter == 'nfs':
            file_list = [i['Mount Point'] for i in file_list
                         if 'nfs' in i['Type'].lower()]
        else:
            file_list = [i['Mount Point'] for i in file_list]
    return file_list


def write_config(conf=None, path=None):
    """

    :param conf:
    :param path:
    :return:
    """
    path = path + "/rackn"
    if not os.path.isdir(path):
        os.makedirs(path)
    path = path + "/drpy.conf"
    with open(path, 'x') as config:
        config.write(conf)
    pass
