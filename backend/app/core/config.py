import datetime
from pathlib import Path
from typing import Annotated, ClassVar
from zoneinfo import ZoneInfo
from pydantic import AmqpDsn, BeforeValidator, ClickHouseDsn, PostgresDsn, RedisDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_ENV_DIR / ".env", _ENV_DIR / ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    {% if event_bus_consumer == "faststream" %}
    FASTSTREAM_PREFETCH_COUNT: int = 1
    FASTSTREAM_INBOX_TTL: datetime.timedelta = datetime.timedelta(days=1)
    {% endif %}
    {%- if db == 'postgres' %}
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = ""
    POSTGRES_SCHEMA: str = "public"
    POSTGRES_DSN: str = ""

    @field_validator("POSTGRES_DSN", mode="before")
    @classmethod
    def postgres_dsn(cls, v: str, values: ValidationInfo) -> str:
        if v:
            return str(PostgresDsn(v))
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=values.data.get("POSTGRES_USER"),
                password=values.data.get("POSTGRES_PASSWORD"),
                host=values.data.get("POSTGRES_HOST"),
                port=values.data.get("POSTGRES_PORT"),
                path=f"{values.data.get('POSTGRES_DB') or ''}",
            )
        )
    {% endif %}
    {%- if broker == "rabbitmq" %}
    RABBITMQ_USER: str = ""
    RABBITMQ_PASSWORD: str = ""
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_QUEUE: str = "{{ project_slug }}"
    RABBITMQ_DSN: str = ""

    @field_validator("RABBITMQ_DSN", mode="before")
    @classmethod
    def rabbitmq_dsn(cls, v: str, values: ValidationInfo) -> str:
        if v:
            return str(AmqpDsn(v))
        return str(
            AmqpDsn.build(
                scheme="amqp",
                username=values.data.get("RABBITMQ_USER"),
                password=values.data.get("RABBITMQ_PASSWORD"),
                host=values.data.get("RABBITMQ_HOST", "localhost"),
                port=values.data.get("RABBITMQ_PORT"),
            )
        )
    {% endif %}
    {%- if cache == "redis" %}
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DSN: str = ""

    @field_validator("REDIS_DSN", mode="before")
    @classmethod
    def redis_dsn(cls, v: str, values: ValidationInfo) -> str:
        if v:
            return str(RedisDsn(v))
        return str(
            RedisDsn.build(
                scheme="redis",
                host=values.data.get("REDIS_HOST", "localhost"),
                port=values.data.get("REDIS_PORT"),
            )
        )
    {% endif %}
    {%- if analytics == "clickhouse" %}
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 9000
    CLICKHOUSE_USER: str
    CLICKHOUSE_PASSWORD: str
    CLICKHOUSE_DB: str
    CLICKHOUSE_DSN: str = ""

    @field_validator("CLICKHOUSE_DSN", mode="before")
    @classmethod
    def clickhouse_dsn(cls, v: str, values: ValidationInfo) -> str:
        if v:
            return str(ClickHouseDsn(v))
        return str(
            ClickHouseDsn.build(
                scheme="clickhouse+asynch",
                username=values.data.get("CLICKHOUSE_USER"),
                password=values.data.get("CLICKHOUSE_PASSWORD"),
                host=values.data.get("CLICKHOUSE_HOST", "localhost"),
                port=values.data.get("CLICKHOUSE_PORT"),
                path=f"{values.data.get('CLICKHOUSE_DB') or ''}",
            )
        )
    {% endif %}
    {%- if ingress != 'no' %}
    API_GATEWAY_URL: str = ""
    {% endif %}
    API_GATEWAY_PATH: str = ""
    DEBUG: bool = True
    INSTALLED_APPS: ClassVar = [
        "dal",
        {%- if event_bus_consumer == "faststream" %}
        "faststream_inbox",{% endif %}
    ]
    PROJECT_NAME: str
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
    SENTRY_DSN: str = ""
    SERVER_TZ: Annotated[ZoneInfo, BeforeValidator(lambda x: ZoneInfo(x) if isinstance(x, str) else x)] = ZoneInfo(
        "Europe/Moscow"
    )

    LOGGING_LEVEL: str = "DEBUG"
    LOGGING_JSON: bool = False


settings = Settings()
