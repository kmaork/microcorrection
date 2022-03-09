from .utils import get


def test_home(client):
    get(client, '/')
