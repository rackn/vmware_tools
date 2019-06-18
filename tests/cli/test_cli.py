from cli.cli import build_arg_parser


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
