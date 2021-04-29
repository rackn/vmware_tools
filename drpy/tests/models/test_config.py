import uuid

import pytest

from drpy.models.config import Config
from drpy.models.config import ConfigException
from drpy.models.config import parse


def test_asdict():
    """_asdict() should return a dictionary."""
    uid = uuid.uuid1()
    ep = "https://foo.com/v1"
    tok = "mytoken"
    conf = Config(ep, tok, uid)
    conf_dict = conf._asdict()
    expected = {
        'endpoint': ep,
        'token': tok,
        'machine_uuid': uid,
        'command_path': None,
        'command_timeout': None,
        'machine_wait': 'wait=10m',
        'duration': '60',
        'last_updated': None,
        'never_update_token': False
    }
    assert conf_dict == expected


def test_replace():
    """_replace() should change passsed in fields"""
    c_bef = Config("foo", "bar", "baz")
    c_after = c_bef._replace(endpoint="foobar")
    c_exp = Config("foobar", "bar", "baz")
    assert c_after == c_exp


def test_defaults():
    """Using no params should invoke defaults"""
    c1 = Config()
    c2 = Config(None, None, None, None, None)
    assert c1 == c2


def test_member_access():
    """Check .field functionality of namedtuple."""
    c = Config("foo", "bar", "baz")
    assert c.endpoint == "foo"
    assert c.token == "bar"
    assert c.machine_uuid == "baz"


def test_parse_raises_exception_for_bad_file():
    with pytest.raises(ConfigException) as ex:
        parse("badfile")

    assert ex.value.args[0] == 'Unable to read badfile'


def test_parse_rasies_ex_for_missing_section(get_dir_path):
    dir_path = get_dir_path
    conf_file = dir_path + "bad_conf.conf"
    with pytest.raises(ConfigException) as ex:
        parse(conf_file)
    assert ex.value.args[0] == '{} missing [Config] section.'.format(conf_file)
