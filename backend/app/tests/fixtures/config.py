from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from core.config import Settings


@pytest.fixture(scope="session")
def app_settings() -> Settings:
    from core.config import settings

    return settings
