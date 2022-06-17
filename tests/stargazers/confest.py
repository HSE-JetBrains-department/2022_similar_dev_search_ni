import pytest


def pytest_addoption(parser):
    """
    Adds option when run from command line.
    """
    parser.addoption("--key", action="store")


@pytest.fixture(scope='session')
def key(request):
    """
    Applies option.
    """
    name_value = request.config.option.key
    if name_value is None:
        pytest.skip()
    return name_value
