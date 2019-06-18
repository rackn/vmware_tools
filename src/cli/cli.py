import argparse
import os


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
        required=False,
        action='store',
        help="Location of config file"
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
