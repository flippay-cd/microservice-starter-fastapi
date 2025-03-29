import os
from collections.abc import Iterable

import pytest
from pytest_asyncio import is_async_test


def setup_env() -> None:
    """
    Redefining environment variables for tests
    """
    # !!! Important: must be before importing application code
    os.environ["POSTGRES__DB"] = "test_db"
    os.environ["RABBITMQ__QUEUE"] = "test_queue"


setup_env()

pytest_plugins: list[str] = [
    "tests.fixtures",
]


def pytest_collection_modifyitems(items: Iterable[pytest.Item]) -> None:
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)
