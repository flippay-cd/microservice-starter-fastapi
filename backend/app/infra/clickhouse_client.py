from typing import cast

from asynch.connection import Connection
from asynch.cursors import DictCursor


class ClickHouseClient:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.connection = Connection(dsn)

    async def connect(self) -> None:
        await self.connection.connect()

    async def disconnect(self) -> None:
        await self.connection.close()

    async def select(self, query: str) -> list[dict]:
        async with self.connection.cursor(cursor=DictCursor) as cursor:
            await cursor.execute(query)
            result = await cursor.fetchall()
        return cast("list[dict]", result)

    async def insert(self, query: str, data: dict) -> int:
        async with self.connection.cursor(cursor=DictCursor) as cursor:
            result = await cursor.execute(query, [data])
        return cast("int", result)
