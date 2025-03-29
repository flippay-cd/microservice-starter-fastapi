import logging
from typing import Self

import httpx

from dal.interfaces import IHttpClient

logger = logging.getLogger(__name__)


class AsyncHttpClient(IHttpClient):
    def __init__(self, host: str, timeout: int = 30):
        self._host = host
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def get(self, url: str, params: dict | None = None, headers: dict | None = None) -> httpx.Response:
        return await self._request(method="GET", url=url, params=params, headers=headers)

    async def post(self, url: str, body: dict | None = None, headers: dict | None = None) -> httpx.Response:
        return await self._request(method="POST", url=url, body=body, headers=headers)

    async def _request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        body: dict | None = None,
        headers: dict | None = None,
        **kwargs,
    ) -> httpx.Response:
        assert self._client
        return await self._client.request(
            method, url=url, params=params, json=body, headers=headers, timeout=self._timeout, **kwargs
        )

    async def __aenter__(self) -> Self:
        if self._client is None:
            logger.info("Устанавливаю соединение с %s...", self._host)
            self._client = httpx.AsyncClient(base_url=self._host, timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client is not None:
            logger.info("Закрываю соединение с %s", self._host)
            await self._client.aclose()
