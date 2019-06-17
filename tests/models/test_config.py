import uuid

from models.config import Config


def test_asdict():
    """_asdict() should return a dictionary."""
    uid = uuid.uuid1()
    ep = "https://foo.com/v1"
    tok = "mytoken"
    conf = Config(ep, tok, uid)
    conf_dict = conf._asdict()
    expected = {'endpoint': ep, 'token': tok, 'machine_uuid': uid}
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
    c2 = Config(None, None, None)
    assert c1 == c2


def test_member_access():
    """Check .field functionality of namedtuple."""
    c = Config("foo", "bar", "baz")
    assert c.endpoint == "foo"
    assert c.token == "bar"
    assert c.machine_uuid == "baz"
