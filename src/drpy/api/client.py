import base64
import json
import ssl
import urllib.request

from drpy.api import __version__


class Client:
    """Basic api client for drp api"""

    def __init__(self, endpoint=None, token=None, machine_uuid=None,
                 insecure=True):
        """

        :type endpoint: str
        :param endpoint: expecting something like: https://drp.local/api/v3
        :type token: str
        :param token:
        :type machine_uuid: str
        :param machine_uuid:
        :type insecure: bool
        :param insecure:
        """
        if endpoint is not None and endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        self.endpoint = endpoint
        self.token = token
        self.machine_uuid = machine_uuid
        self.insecure = insecure

        if self.insecure:
            self.context = self.setup_insecure()
        self.headers = {
            "User-Agent": "drpy v{} (https://github.com/rackn/drpy)".format(
                __version__
            ),
            "Accept": "application/json"
        }
        if token is not None:
            self.setup_token_auth(token)

    def setup_token_auth(self, token):
        self.headers.pop("Authorization", None)
        self.headers.update(
            {"Authorization": "Bearer {}".format(token)}
        )

    def setup_basic_auth(self, user, passwd):
        """

        :type user: str
        :param user:
        :type passwd: str
        :param passwd:
        :return:
        """
        self.headers.pop("Authorization", None)
        string = "{}:{}".format(user, passwd)
        b64str = base64.standard_b64encode(string.encode('utf-8'))

        self.headers.update(
            {"Authorization": "Basic {}".format(b64str.decode("utf-8"))}
        )

    @staticmethod
    def setup_insecure():
        """
        Sets up a context to use for ignoring invalid SSL
        """
        ctx = ssl.create_default_context()
        ctx.set_ecdh_curve("secp384r1")
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def get(self, resource=None):
        """
        Primitive get request that will return a json_decoded
        object of the resource. The actual type will vary depending
        on what the API returns.

        :type resource: str
        :param resource: An API resource like: info, objects, machines, etc..
        :return:
        """
        url = self.endpoint + "/{}".format(resource)
        r = urllib.request.Request(url, headers=self.headers)
        res = urllib.request.urlopen(r, context=self.context)
        data = res.read().decode('utf-8')
        json_obj = json.loads(data)
        return json_obj
