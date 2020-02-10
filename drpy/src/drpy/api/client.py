import base64
import json
import ssl
import time
import urllib.request

from drpy.api import __version__
from drpy import logger


class Client:
    """Basic api client for drp api"""

    def __init__(self, endpoint=None, token=None, insecure=True):
        """
        Initialize a new Client to use to talk to the drp api

        :type endpoint: str
        :param endpoint: expecting something like: https://drp.local/api/v3
        :type token: str
        :param token:
        :type insecure: bool
        :param insecure:
        """
        if endpoint is not None and endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        if endpoint is not None and not endpoint.endswith("/api/v3"):
            endpoint = endpoint + "/api/v3"
        self.endpoint = endpoint
        self.token = token

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
        """
        Adds the token based header. This method is called
        automatically if you create a Client() with a token
        Ex:
        client = Client(token="mytoken")

        When you call this method it will remove the previous
        `Authorization` header.

        To get a token to use see `drpcli users token <username>`

        :type token: str
        :param token:
        :return:
        """
        self.headers.pop("Authorization", None)
        self.headers.update(
            {"Authorization": "Bearer {}".format(token)}
        )

    def setup_basic_auth(self, user, passwd):
        """
        Adds the required headers to support basic auth.
        Calling this method will remove previous
        `Authorization` header and replace it with the
        Basic header.

        :type user: str
        :param user:
        :type passwd: str
        :param passwd:
        :return: void
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
        retry_count = 0
        while retry_count < 31536000:
            try:
                res = urllib.request.urlopen(r, context=self.context)
                data = res.read().decode('utf-8')
                json_obj = json.loads(data)
                return json_obj
            except urllib.error.URLError as e:
                time.sleep(5)
                retry_count = retry_count + 1
                saved_error = e
        raise saved_error

    def patch(self, resource=None, payload=None):
        """
        Given a resource and a payload of an RFC6902 patch
        make a PATCH request to update the given resource with
        the given payload.

        Example:
        obj = client.patch(
              resource="machines/6d109287-dffa-4344-a727-2b17970ca210",
              payload=payload)

        :type resource: str
        :param resource: machines/uuid, jobs/uuid, etc..
        :type payload: str
        :param payload: '[{"value": "b", "op": "replace", "path": "/1"},
                          {"value": "v", "op": "replace", "path": "/2"}]'
        :return: python object
        """
        url = self.endpoint + "/{}".format(resource)
        jsondata = json.loads(payload)
        jsondata = json.dumps(jsondata)
        jsonbytes = jsondata.encode('utf-8')
        headers = self.headers
        headers.update({"Content-Type": "application/json; charset=utf-8"})
        r = urllib.request.Request(url, data=jsonbytes, headers=headers,
                                   method="PATCH")
        try:
            res = urllib.request.urlopen(r, context=self.context)
            data = res.read().decode('utf-8')
            json_obj = json.loads(data)
            return json_obj
        except urllib.error.HTTPError as res:
            logger.debug("Failed to patch.")
            logger.debug("Resource: {}".format(url))
            logger.debug("Payload: {}".format(jsonbytes))
            logger.exception(res)
            return {'Error': res.code}

    def post_job(self, payload=None):
        """
        Post an empty job to the drp api
        to get a new job.

        :type payload: dict
        :param payload: Python dict containing a models.job.Job
                        with a machine uuid set.
        :return:
        """
        resource = self.endpoint + "/jobs"
        if payload is None:
            raise ValueError("payload can not be None type.")
        payload = json.dumps(payload)
        jsonbytes = payload.encode('utf-8')
        headers = self.headers
        headers.update({"Content-Type": "application/json; charset=utf-8"})
        r = urllib.request.Request(resource, data=jsonbytes, headers=headers,
                                   method="POST")
        try:
            res = urllib.request.urlopen(r, context=self.context)
            logger.debug("POST_JOB Response: {} {}".format(
                res.status,
                res.msg
            ))
            if res.status == 204:
                return {}
            data = res.read().decode('utf-8')
            json_obj = json.loads(data)
            return json_obj
        except urllib.error.HTTPError as res:
            return {'Error': res.code}
            pass

    def put_job_log(self, job=None, log_msg=None):
        """
        POST a log message to DRP about a given job.

        :type job: Job
        :param job:
        :type log_msg: str
        :param log_msg:
        :return:
        """
        if job is None:
            raise ValueError("job can not be None.")
        if log_msg is None:
            raise ValueError("log_message can not be None")
        resource = self.endpoint + "/jobs/{}/log".format(job)
        log_msg = log_msg.encode("utf-8")
        headers = self.headers
        headers.update({"Content-Type": "application/octet-stream"})
        r = urllib.request.Request(resource, data=log_msg, headers=headers,
                                   method="PUT")
        try:
            res = urllib.request.urlopen(r, context=self.context)
            logger.debug("PUT_JOB_LOG Response: {} {}".format(
                res.status,
                res.msg
            ))
            if res.status == 204:
                return True
        except urllib.error.HTTPError:
            return False
        return False
