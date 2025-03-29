from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from core.config import Settings


@pytest.fixture(scope="session")
def async_db_database_url(app_settings: Settings) -> str:
    return app_settings.POSTGRES_DSN
