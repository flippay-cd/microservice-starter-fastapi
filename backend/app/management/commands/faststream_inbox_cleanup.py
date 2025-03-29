import asyncio
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from dependency_injector.wiring import Provide, inject
from faststream_inbox.interface import IInboxDAO

from core.config import settings
from core.container import Container


@inject
async def command(
    inbox_dao: IInboxDAO = Provide[Container.dao_inbox],
    transaction: Callable[[], AbstractAsyncContextManager] = Provide[Container.dao_transaction],
) -> None:
    async with transaction():
        await inbox_dao.cleanup(ttl=settings.FASTSTREAM_INBOX_TTL)


if __name__ == "__main__":
    container = Container()
    container.wire(modules=[__name__])
    asyncio.run(command())
