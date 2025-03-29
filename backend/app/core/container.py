from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dependency_injector import containers, providers
{%- if ingress != 'no' %}
from exp_auth import AuthAPI
from exp_auth.jwt import create_eddsa_jwt_decoder
{%- endif %}
{%- if db == 'postgres' %}
from exp_async_db.database import Database
{%- endif %}
{%- if event_bus_consumer == 'faststream' %}
from faststream.rabbit import RabbitBroker
from faststream_inbox.dao import DBInboxDAO
{%- endif %}
{% if ingress != 'no' %}
from controllers.auth.api_gateway_jwt import ApiGatewayJWTAuth
{%- endif %}
from controllers.healthcheck import HealthCheckController
from controllers.metrics import MetricsController

from .config import settings


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

{% if db == 'postgres' %}
async def _init_db(**kwargs: Any) -> AsyncIterator[Database]:
    async with Database(**kwargs) as db:
        yield db
{% endif %}

{% if ingress != 'no' %}
async def fetch_api_gateway_signing_key(url: str) -> AsyncIterator[str]:
    if not url:
        yield ""
    else:
        async with AuthAPI(url) as client:
            key = await client.get_jwk()

        yield key
{% endif %}

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["api"{%- if event_bus_consumer == 'faststream' %}, "streams"{%- endif %}]
    )

    config = providers.Configuration()
    config.from_dict(settings.model_dump())

    {% if db == 'postgres' %}
    # Database
    db = providers.Resource(_init_db, db_url=config.POSTGRES_DSN, schema=config.POSTGRES_SCHEMA)
    db_session_factory = providers.Singleton(db.provided.session_factory)
    {%- endif %}

    {% if event_bus_consumer == 'faststream' -%}
    # Faststream
    faststream_broker = providers.Singleton(
        RabbitBroker,
        url=config.RABBITMQ_DSN,
        max_consumers=config.FASTSTREAM_PREFETCH_COUNT,
        graceful_timeout=5,
    )
    {% endif %}
    # DAO
    {%- if event_bus_consumer == 'faststream' %}
    dao_inbox = providers.Factory(DBInboxDAO, db=db.provided)
    {%- endif %}
    dao_transaction = providers.Factory(db.provided.transaction)

    # Services
    # ...

    # Controllers
    healthcheck_healthcheck_controller = providers.Factory(HealthCheckController)
    metrics_metrics_controller = providers.Factory(MetricsController)
    {% if ingress != 'no' %}
    # Auth
    jwt_public_key = providers.Resource(fetch_api_gateway_signing_key, url=config.API_GATEWAY_URL)
    jwt_decoder = providers.Factory(create_eddsa_jwt_decoder, jwt_public_key)
    process_auth_token_bearer = providers.Factory(ApiGatewayJWTAuth, decoder=jwt_decoder)
    {% endif %}
