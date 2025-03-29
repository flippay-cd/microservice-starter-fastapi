import pytest

from core.container import Container


@pytest.fixture(scope="session")
def container():
    return Container()
