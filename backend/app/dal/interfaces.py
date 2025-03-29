from abc import ABC, abstractmethod
from typing import Self

import httpx


class IHttpClient(ABC):
    @abstractmethod
    async def __aenter__(self) -> Self:  # pragma: no cover
        ...

    @abstractmethod
    async def __aexit__(self, *exc):  # pragma: no cover
        ...

    @abstractmethod
    async def get(self, url: str, params: dict | None = None) -> httpx.Response:  # pragma: no cover
        ...

    @abstractmethod
    async def post(self, url: str, body: dict | None = None) -> httpx.Response:  # pragma: no cover
        ...
