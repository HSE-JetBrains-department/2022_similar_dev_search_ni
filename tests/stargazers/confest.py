import pytest


def pytest_addoption(parser):
    parser.addoption("--key", action="store")


@pytest.fixture(scope='session')
def key(request):
    name_value = request.config.option.key
    if name_value is None:
        pytest.skip()
    return name_value
