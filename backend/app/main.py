from __future__ import annotations

import logging.config
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import sentry_sdk
from fastapi import FastAPI as BaseFastAPI
from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError

import logging_conf
from api.healthcheck.router import api_router as healthcheck_router
from api.metrics.router import api_router as metrics_router
from api.v1.router import api_router as v1_router
from core.config import settings
from core.container import Container
from services.exceptions import NotFoundError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logging.config.dictConfig(logging_conf.LOGGING)

logger = logging.getLogger(__name__)

sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.01)


class FastAPI(BaseFastAPI):
    container: Container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    container = app.container

    resource_initializer = container.init_resources()
    if resource_initializer:
        logger.info("Инициализирую ресурсы...")
        await resource_initializer

    yield

    resource_finalizer = container.shutdown_resources()
    if resource_finalizer:
        logger.info("Освобождаю ресурсы...")
        await resource_finalizer


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    root_path=settings.API_GATEWAY_PATH,
    debug=settings.DEBUG,
)
app.container = Container()


@app.exception_handler(ValidationError)
async def validation_exception_handler(_request: Request, exc: ValidationError) -> ORJSONResponse:
    return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.errors()})


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(_request: Request, exc: NotFoundError) -> ORJSONResponse:
    return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.errors()})


# set middlewares
# ...

# set routers
app.include_router(v1_router, prefix="/api")
app.include_router(healthcheck_router)
app.include_router(metrics_router)
