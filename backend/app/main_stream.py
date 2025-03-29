import logging.config

import sentry_sdk
from faststream.asgi import AsgiFastStream, make_ping_asgi

import logging_conf
from core.config import settings
from core.container import Container

# TODO: replace with container's Resource provider
#  (https://python-dependency-injector.ets-labs.org/providers/resource.html)
logging.config.dictConfig(logging_conf.LOGGING)

sentry_sdk.init(dsn=settings.SENTRY_DSN, enable_tracing=True)

container = Container()
broker = container.faststream_broker()
app = AsgiFastStream(
    broker,
    asgi_routes=[
        ("/healthcheck", make_ping_asgi(broker, timeout=5.0)),
    ],
    asyncapi_path="/docs",
)
