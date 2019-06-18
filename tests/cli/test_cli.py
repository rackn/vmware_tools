import os
from cli.cli import build_arg_parser, verify_conf_file


def test_short_arg():
    """using a short arg should expand to the long opt"""
    args = ['-fmyconfig.yml']
    parser = build_arg_parser()
    parsed = parser.parse_args(args)
    assert parsed.conf_file == "myconfig.yml"


def test_long_arg():
    """Using the long opt should expand to the long opt"""
    args = ['--conf_file=myconfig.yml']
    parser = build_arg_parser()
    parsed = parser.parse_args(args)
    assert parsed.conf_file == "myconfig.yml"


def test_conf_file_true_with_valid_info():
    """When given a valid file one can read make sure we get True"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    conf_file = dir_path + "/../fixtures/example_config.conf"
    assert verify_conf_file(conf_file)
