from pytest import fixture
from microserver.views import app as micro_app

from .levels import levels, Level, new_orleans


@fixture
def client():
    return micro_app.test_client()


@fixture(params=levels)
def level(request):
    return request.param


@fixture
def example_level() -> Level:
    return new_orleans
