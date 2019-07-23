import pytest

from drpy.api.client import Client


@pytest.fixture()
def setup_client():
    end_point = "https://192.168.1.53:8092"
    client = Client(endpoint=end_point)
    client.setup_basic_auth("rocketskates", "passthis")
    return client
