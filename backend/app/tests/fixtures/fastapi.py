from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from exp_async_db.database import Database

    from main import FastAPI


@pytest.fixture(scope="session")
async def app(async_db_database: Database) -> AsyncGenerator[FastAPI, None]:
    from main import app as fastapi_app

    with fastapi_app.container.db.override(async_db_database):
        yield fastapi_app


@pytest.fixture
def test_client_anonymous(app: FastAPI) -> TestClient:
    return TestClient(app)
