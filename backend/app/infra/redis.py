from typing import Any

import redis.asyncio as redis


class RedisClient:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.client = redis.Redis.from_url(dsn, decode_responses=True)

    async def disconnect(self) -> None:
        await self.client.aclose()

    async def set(self, key: str, value: Any) -> None:
        await self.client.set(key, value)

    async def get(self, key: str) -> Any:
        return await self.client.get(key)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)
