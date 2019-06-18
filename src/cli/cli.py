import argparse


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
